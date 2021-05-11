import json
import re
import unittest
from pathlib import Path
from typing import List, Union, Optional
from subprocess import check_call, run, Popen, PIPE, CalledProcessError, \
    check_output

_header_prefix: Optional[str] = None


def print_header(s: str) -> None:
    global _header_prefix
    print()
    print('/' * 80)
    if _header_prefix is not None:
        print('  ' + _header_prefix)

    print('  ' + s.upper())
    print('/' * 80)
    print()


def set_header_prefix(suffix: str):
    global _header_prefix
    _header_prefix = suffix


def _combine(items: List) -> List[str]:
    args: List[str] = list()
    for item in items:
        if isinstance(item, str):
            args.append(item)
        elif isinstance(item, list) or isinstance(item, tuple):
            args.extend(item)
        elif item is None:
            continue
        else:
            raise TypeError(item)
    return args


def docker_build(source_dir: Path, image_name: str,
                 docker_file: Path = None) -> None:
    print_header(f'Building docker image {image_name}')
    args = _combine([
        'docker', 'build', '-t', image_name,
        ['-f', str(docker_file)] if docker_file else None,
        str(source_dir)
    ])
    check_call(args)


def docker_run(image_name: str, container_name: str = None,
               detach: bool = False,
               port_host: int = None,
               port_docker: int = None):
    print_header(
        f"Starting docker image {image_name} (container: {container_name})")

    if port_host is not None or port_docker is not None:
        if port_host is None or port_docker is None:
            raise ValueError(
                "Both or none of [port_host, port_docker] must be specified")
        port_mapping = str(port_host) + ':' + str(port_docker)
    else:
        port_mapping = None

    command = _combine([
        'docker', 'run', '--rm',
        '-d' if detach else None,
        ('-p', port_mapping) if port_mapping else None,
        ('--name', container_name) if container_name else None,
        image_name])

    check_call(command)


def docker_stop(container_name: str):
    print_header(f"Stopping docker container {container_name}")
    check_call(('docker', 'container', 'stop', container_name))


class EcrRepoUri:
    def __init__(self, uri: str):
        self.uri = uri

        m = re.match(r'(.+)/([^@:]+)(?:[@:](.+))?', uri)
        self.host = str(m.group(1))
        self.name = str(m.group(2))
        self.tag = str(m.group(3)) if m.group(3) else None
        self.region = self.host.split('.')[-3]

    @property
    def uri_without_tag(self):
        return self.host + '/' + self.name

    def __str__(self):
        return self.uri


class TestEctRepoUri(unittest.TestCase):
    def test_with_tag(self):
        src = '1253812538.dkr.ecr.us-east-1.amazonaws.com/abc_x1:mytag'
        uri = EcrRepoUri(src)
        self.assertEqual(uri.host, '1253812538.dkr.ecr.us-east-1.amazonaws.com')
        self.assertEqual(uri.name, 'abc_x1')
        self.assertEqual(uri.tag, 'mytag')
        self.assertEqual(uri.region, 'us-east-1')
        self.assertEqual(uri.uri_without_tag,
                         '1253812538.dkr.ecr.us-east-1.amazonaws.com/abc_x1')

    def test_without_tag(self):
        src = '1253812538.dkr.ecr.us-east-1.amazonaws.com/abc_x1'
        uri = EcrRepoUri(src)
        self.assertEqual(uri.host, '1253812538.dkr.ecr.us-east-1.amazonaws.com')
        self.assertEqual(uri.name, 'abc_x1')
        self.assertEqual(uri.region, 'us-east-1')
        self.assertEqual(uri.tag, None)
        self.assertEqual(uri.uri_without_tag,
                         '1253812538.dkr.ecr.us-east-1.amazonaws.com/abc_x1')

    def test_with_sha(self):
        src = '61298361286.dkr.ecr.us-east-1.amazonaws.com' \
              '/imagename@sha256:d13b68bf5763e3cf8b9898d4c2b' \
              '5000ad538e8d4155ef80686e0c3f04322c9af'
        uri = EcrRepoUri(src)
        self.assertEqual(uri.name, 'imagename')
        self.assertTrue(uri.tag.startswith('sha256:d13b68'))


def ecr_repo_uri_to_region(uri: str) -> str:
    parts = uri.split('/')
    host = next(p for p in parts if p.endswith('.amazonaws.com'))
    return host.split('.')[-3]


assert ecr_repo_uri_to_region(
    "1253812538.dkr.ecr.us-east-1.amazonaws.com/abc") == 'us-east-1'


def _get_digest(output: str) -> str:
    m = re.search(r'digest: (sha256:[0-9a-z]+)', output)
    return str(m.group(1))


class TestGetDigest(unittest.TestCase):
    def test(self):
        s = _get_digest('''
            30472d65e424: Pushed
            95e3c2813def: Pushed
            latest: digest: sha256:d4c7852abfabaf3076bd6a84 size: 2841
        ''')
        self.assertEqual(s, 'sha256:d4c7852abfabaf3076bd6a84')


def ecr_delete_images_by_json(repo_uri: Union[EcrRepoUri, str],
                              image_ids_in_json: str):
    if isinstance(repo_uri, str):
        repo_uri = EcrRepoUri(repo_uri)

    if not json.loads(image_ids_in_json):
        print("Nothing to delete")
        return

    check_call(('aws', 'ecr', 'batch-delete-image',
                '--region', repo_uri.region,
                '--repository-name', repo_uri.name,
                '--image-ids', image_ids_in_json))


def ecr_delete_images_all(repo_uri: str):
    print_header(f"Deleting all images from {str(repo_uri)}")

    repo_uri = EcrRepoUri(repo_uri)

    js = check_output((
        'aws', 'ecr', 'list-images',
        '--region', repo_uri.region,
        '--repository-name', repo_uri.name,
        '--query', 'imageIds[*]',
        '--output', 'json'

    ), encoding="utf-8")

    ecr_delete_images_by_json(repo_uri, js)


def docker_push_to_ecr(docker_image: str,
                       repo_uri: Union[EcrRepoUri, str]):
    """
    :param repo_uri: '1253812538.dkr.ecr.us-east-1.amazonaws.com/abc:mytag'
    :param docker_image: 'abc:mytag'

    When we push abc:mytag, it will be accessible with both
    1) ...amazonaws.com/abc:mytag (the repo_uri)
    2) ...amazonaws.com/abc@sha256:...

    The function returns the second one.
    """

    if isinstance(repo_uri, str):
        repo_uri = EcrRepoUri(repo_uri)

    with Popen(
            ('aws', 'ecr', 'get-login-password',
             '--region', repo_uri.region),
            stdout=PIPE) as get_password:
        check_call(
            ('docker', 'login',
             '--username', 'AWS',
             '--password-stdin',
             repo_uri.host),
            stdin=get_password.stdout)

    check_call((
        'docker', 'tag', docker_image,
        repo_uri.uri_without_tag
    ))

    cp = run((
        'docker', 'push', repo_uri.uri
    ),
        capture_output=True,
        encoding='utf-8')
    if cp.returncode != 0:
        raise CalledProcessError(cp.returncode, cp.args)

    digest = _get_digest(cp.stdout)
    alternate_image_uri = repo_uri.uri_without_tag + '@' + digest
    print(f"Pushed image URI: {alternate_image_uri}")
    return alternate_image_uri


def lambda_function_wait_updated(aws_region: str, func_name: str):
    # Waits for the function's LastUpdateStatus to be Successful.
    # It will poll every 5 seconds until a successful state has
    # been reached. This will exit with a return code of 255 after
    # 60 failed checks
    print(f"Waiting for successful update status "
          f"of {func_name} at {aws_region}", flush=True)
    check_call((
        'aws', 'lambda', 'wait', 'function-updated',
        '--region', aws_region,
        '--function-name', func_name))


def lambda_function_update(aws_region: str, func_name: str, ecr_image_uri: str):
    # ecr_image_uri can be an uri with hash code:
    # 61298361286.dkr.ecr.us-east-1.amazonaws.com/imagename@sha256:d13b68bf5763e3cf8b9898d4c2b5000ad538e8d4155ef80686e0c3f04322c9af

    print_header(f"Updating function {func_name}")

    print(f"Function: {func_name} at {aws_region}")
    print(f"Image: {ecr_image_uri}")
    print()

    # when we call update-function-code twice in a row,
    # we can get "The operation cannot be performed at this time.
    # An update is in progress for resource". So we'll wait here...
    lambda_function_wait_updated(aws_region, func_name)

    check_call((
        'aws', 'lambda', 'update-function-code',
        '--region', aws_region,
        '--function-name', func_name,
        '--image-uri', ecr_image_uri
    ))

    lambda_function_wait_updated(aws_region, func_name)
    print_header(f"Function {func_name} updated")


if __name__ == "__main__":
    unittest.main()

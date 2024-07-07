from __future__ import annotations

import sys

from pip_constraint_helpers import (
    get_constraint_file_path,
    get_runtime_python_tag,
    run_cmd,
)


def generate_lock_for(
    req_dir: str, toxenv: str, *pip_compile_extra_args: tuple[str, ...],
) -> None:
    lock_file_name = get_constraint_file_path(
        req_dir, toxenv, get_runtime_python_tag(),
    )
    direct_deps_file_name = lock_file_name.with_name(f'tox-{toxenv}.in')
    pip_compile_cmd = (
        sys.executable, '-Im', 'piptools', 'compile',
        f'--output-file={lock_file_name !s}',
        str(direct_deps_file_name),
        *pip_compile_extra_args,
    )
    run_cmd(pip_compile_cmd)


if __name__ == '__main__':
    generate_lock_for(*sys.argv[1:])

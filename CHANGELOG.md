## [v1.2](https://github.com/sbidoul/whool/tree/v1.1.1) - 2024-07-25


### Bugfixes

- When then `git` command is not available, copy all files to distribution
  package ([#23](https://github.com/sbidoul/whool/issues/23))


## [v1.1](https://github.com/sbidoul/whool/tree/v1.1) - 2024-07-18


### Features

- `whool init` now accepts a directory argument ([#21](https://github.com/sbidoul/whool/issues/21))


## [v1.0.1](https://github.com/sbidoul/whool/tree/v1.0.1) - 2024-03-18

## Bug fixes

- Previous build was missing the `whool` script.

## [v1.0](https://github.com/sbidoul/whool/tree/v1.0) - 2024-03-16


### Features

- Allow building from outside a git directory. This requires pip>=21.3. ([#18](https://github.com/sbidoul/whool/issues/18))


## [v0.5](https://github.com/sbidoul/whool/tree/v0.5) - 2023-10-28


### Features

- Print modified content when `whool init` exits non-zero. ([#15](https://github.com/sbidoul/whool/issues/15))


## [v0.4](https://github.com/sbidoul/whool/tree/v0.4) - 2023-10-21

`whool` is now considered stable. A 1.0 will be released when the documentation is
complete and the test coverage improved a bit.

### Features

- When doing an editable install, add a `.gitignore` file in the `build` directory. ([#7](https://github.com/sbidoul/whool/issues/7))
- Add pre-commit hook to initialize `pyproject.toml`. ([#10](https://github.com/sbidoul/whool/issues/10))
- Test with python 3.12. ([#11](https://github.com/sbidoul/whool/issues/11))

### Docs

- Improved documentation in README.

# Godot Rust GDExtension Copier template

A reusable version of the `gf_clouds` repository's Rust/Godot development and
release scaffold. Generated projects contain a minimal native node with an
exported property, an editor-only plugin, a runnable Godot sandbox, and native
build and packaging helpers.

## Generate a project

Install [Copier](https://copier.readthedocs.io/en/stable/) 9.19 or newer, below 10:

```sh
uv tool install 'copier>=9.19,<10'
copier copy /path/to/GDExtensionTemplate /path/to/my_extension
```

For a noninteractive generation:

```sh
copier copy --defaults \
  --data addon_name=terrain_tools \
  --data project_name='Terrain Tools' \
  --data class_prefix=TerrainTools \
  /path/to/GDExtensionTemplate /path/to/terrain_tools

cd /path/to/terrain_tools
just check
just demo
```

The questions cover the addon/crate name, display name, description, native class
prefix, iOS bundle identifier prefix, and whether to include GitHub Actions.
Names default to `my_extension`, `My Extension`, and `MyExtension`. Set
`--data include_github_actions=false` to omit both workflows and release-please
configuration. Generated projects start at version `0.1.0`.

## Generated project

- `rust/`: pinned godot-rust dependency and lockfile, separate runtime/editor
  modules, optional Web features.
- `addon/`: GDExtension descriptor; build helpers publish native libraries here.
- `godot/`: runnable Compatibility-renderer demo.
- `scripts/`: Python standard-library build, synchronization, packaging, and
  formatting, lint, and Godot import checks.
- `justfile`: `check`, `build-debug`, `build`, `demo`, `editor`, `check-godot`,
  `check-all`, and `package` commands.
- Optional CI and release-please automation on `[self-hosted, macos]` runners,
  cross-compiling the 16 desktop, Android, iOS, and Web release targets.

Prerequisites for generated projects: rustup, Python 3.11+, just, a native
compiler/linker, and Godot 4.7+. The inherited pins are Rust 1.97.1,
godot-rust 0.5.5, and CI Godot 4.7.2. Set `GODOT` to your engine executable
when it is not named `godot` on PATH. Platform SDK requirements and GitHub App
release credentials are documented in each generated project's root README.

Register a macOS self-hosted runner for each generated repository before running
Actions. All jobs require both `self-hosted` and `macos` labels; none select a
GitHub-hosted runner. Runner prerequisites are in the generated root README.

The template omits cloud rendering, shaders, icons, historical changelogs,
cached imports, native binaries, and test suites.
Generation only writes files; building is an explicit step and requires no
Copier `--trust` flag.

## Template maintenance

Generate a project and run `just check-all` and `just package` inside it to
check formatting, lint the Rust code, import the Godot sandbox, and build a
native package. The template and generated projects contain no test suites.

Only `template/` is rendered. Templates use `[[[ variable ]]]` expressions so
Cargo's `[[package]]`, just's `{{ python }}`, and GitHub's `${{ ... }}` survive
unchanged. See [Copier configuration](https://copier.readthedocs.io/en/stable/configuring/)
for the configured environment delimiters and answers file behavior.

For updatable projects, commit and version-tag this template in Git **before**
generating them. Commit the generated `.copier-answers.yml` along with the project,
then run `copier update` from that project's clean Git checkout when a new template
tag is available. An unversioned local directory supports generation, but does not
record the template commit required for updates.

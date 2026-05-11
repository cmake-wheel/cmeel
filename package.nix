{
  lib,
  buildPythonApplication,
  installShellFiles,
  argcomplete,
  cmake,
  git-archive-all,
  hatchling,
  packaging,
  tomli,
  wheel,
}:

buildPythonApplication {
  pname = "cmeel";
  version = "0.60.1";
  pyproject = true;

  src = lib.fileset.toSource {
    root = ./.;
    fileset = lib.fileset.unions [
      ./cmeel
      ./cmeel.pth
      ./cmeel_pth.py
      ./pyproject.toml
      ./README.md
    ];
  };

  nativeBuildInputs = [
    installShellFiles
    argcomplete
  ];

  build-system = [
    hatchling
  ];

  dependencies = [
    tomli
  ];

  optional-dependencies = {
    build = [
      cmake
      git-archive-all
      packaging
      wheel
    ];
    cli = [
      argcomplete
    ];
  };

  pythonImportsCheck = [
    "cmeel"
  ];

  postInstall = ''
    installShellCompletion --cmd cmeel \
      --bash <(register-python-argcomplete --shell bash cmeel) \
      --fish <(register-python-argcomplete --shell fish cmeel) \
      --zsh <(register-python-argcomplete --shell zsh cmeel)

  '';

  meta = {
    description = "Create Wheel from CMake projects";
    homepage = "https://github.com/cmake-wheel/cmeel";
    changelog = "https://github.com/cmake-wheel/cmeel/blob/cmeel/CHANGELOG.md";
    license = lib.licenses.bsd2;
    maintainers = with lib.maintainers; [ nim65s ];
    mainProgram = "cmeel";
  };
}

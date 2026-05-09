{
  lib,
  buildPythonApplication,
  cmake,
  git-archive-all,
  hatchling,
  packaging,
  tomli,
  wheel,
}:

buildPythonApplication {
  pname = "cmeel";
  version = "0.59.0";
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
  };

  pythonImportsCheck = [
    "cmeel"
  ];

  meta = {
    description = "Create Wheel from CMake projects";
    homepage = "https://github.com/cmake-wheel/cmeel";
    changelog = "https://github.com/cmake-wheel/cmeel/blob/cmeel/CHANGELOG.md";
    license = lib.licenses.bsd2;
    maintainers = with lib.maintainers; [ nim65s ];
    mainProgram = "cmeel";
  };
}

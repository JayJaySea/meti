{ pkgs ? import <nixpkgs> {} }:

pkgs.python3Packages.buildPythonApplication {
  pname = "meti";
  version = "0.8.1";
  src = ./.;
  format = "setuptools";

  nativeBuildInputs = with pkgs.python3Packages; [
    setuptools
    wheel
  ];

  propagatedBuildInputs = with pkgs.python3Packages; [
    pyside6
    pillow
    pysqlcipher3
  ];
}

{
  description = "pitext - OCR tool for capturing text from screen regions (Wayland)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };

        pitext = pkgs.python3Packages.buildPythonApplication {
          pname = "pitext";
          version = "0.1.0";
          pyproject = true;

          src = ./.;

          build-system = [ pkgs.python3Packages.hatchling ];

          dependencies = with pkgs.python3Packages; [
            pytesseract
            pyperclip
            pillow
          ];

          # slurp/grim/tesseract are separate CLI tools invoked via subprocess,
          # so they must be on PATH at runtime rather than declared as Python deps.
          nativeBuildInputs = [ pkgs.makeWrapper ];

          postInstall = ''
            wrapProgram $out/bin/pitext \
              --prefix PATH : ${
                pkgs.lib.makeBinPath [
                  pkgs.slurp
                  pkgs.grim
                  pkgs.tesseract
                ]
              }
          '';

          pythonImportsCheck = [ "pytesseract" ];
        };
      in
      {
        packages.default = pitext;
        packages.pitext = pitext;

        apps.default = flake-utils.lib.mkApp { drv = pitext; };

        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.uv
            pkgs.slurp
            pkgs.grim
            pkgs.tesseract
          ];
        };
      }
    );
}

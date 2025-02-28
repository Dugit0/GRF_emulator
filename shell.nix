{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
    packages = [
        pkgs.ghc
        (pkgs.python3.withPackages (python-pkgs: with python-pkgs; [
            pyside6
            lark
            numpy
            pandas
            matplotlib
            seaborn
            jupyter
        ]))
    ];
}

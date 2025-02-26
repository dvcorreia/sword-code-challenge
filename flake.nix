{
  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
  };

  outputs =
    {
      self,
      nixpkgs,
      ...
    }:
    let
      supportedSystems = [
        "aarch64-linux"
        "aarch64-darwin"
        "x86_64-darwin"
        "x86_64-linux"
      ];

      forAllSystems = f: nixpkgs.lib.genAttrs supportedSystems (system: f system);
      nixpkgsFor = forAllSystems (
        system:
        import nixpkgs {
          inherit system;
        }
      );
    in
    {
      devShells = forAllSystems (
        system: with nixpkgsFor.${system}; {
          default = mkShell {
            packages = [
              git
              gnumake
              (python3.withPackages (
                ps: with ps; [
                  pip
                ]
              ))

              dex-oidc
              open-policy-agent
              sqlc
            ];
          };
        }
      );

      formatter = forAllSystems (system: (nixpkgsFor.${system}).nixfmt-rfc-style);
    };
}

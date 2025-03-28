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
          overlays = [ self.overlay ];
        }
      );
    in
    {
      overlay = final: prev: {
        clinical-recommendations = prev.callPackage ./package.nix { };
      };

      packages = forAllSystems (system: {
        default = (nixpkgsFor.${system}).clinical-recommendations;
        oci-image =
          let
            pkgs = (nixpkgsFor.${system});
          in
          pkgs.dockerTools.buildLayeredImage {
            name = "clinical-recommendations";
            tag = "latest";

            contents = [ pkgs.clinical-recommendations ];

            config = {
              Cmd = [ "/bin/clinical_recommendations" ];
              ExposedPorts = {
                "8000/tcp" = { };
              };
            };
          };
      });

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

              duckdb
              redis
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

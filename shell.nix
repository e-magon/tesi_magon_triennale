# Function that accepts pkgs parameter, defaulting to the standard nixpkgs package set
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    python3Packages.pip
    python3Packages.virtualenv
  ];

  shellHook = ''
    # Create a virtual environment if it doesn't exist
    if [ ! -d .venv ]; then
      echo "Creating virtual environment..."
      python -m venv .venv
    fi

    # Activate the virtual environment
    source .venv/bin/activate

    # Install dependencies from requirements.txt
    # if [ -f requirements.txt ]; then
    #   echo "Installing Python dependencies..."
    #   pip install -r requirements.txt
    # fi

    echo "Nix shell ready"
  '';
}

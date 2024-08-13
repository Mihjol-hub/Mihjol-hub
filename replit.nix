{pkgs}: {
  deps = [
    pkgs.python311Full        # python 3.11
    pkgs.sqlite-interactive   # SQLite
    pkgs.nano                 # Nano editor 
    pkgs.python311Packages.flask
    pkgs.python311Packages.sqlalchemy
    pkgs.python311Packages.flask_sqlalchemy
  ];
}

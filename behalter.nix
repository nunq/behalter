{ config, pkgs, lib, ... }: {
  services.nginx = {
    enable = true;
    recommendedTlsSettings = true;    
    recommendedGzipSettings = true;
    recommendedProxySettings = true;
    recommendedOptimisation = true;
    virtualHosts."behalter.domain.tld" = {
      forceSSL = true;
      enableACME = true;
      locations."/" = {
        basicAuth = {
          behalter = lib.removeSuffix "\n" "${builtins.readFile /etc/secrets/basicauth_behalter}";
        };
        extraConfig = ''
          include ${config.services.nginx.package}/conf/uwsgi_params;
          uwsgi_pass ${config.services.uwsgi.instance.socket};

          access_log /var/log/nginx/behalter-access.log;
          error_log  /var/log/nginx/behalter-error.log;
        '';
      };
    };
  };
  services.uwsgi = {
    enable = true;
    plugins = [ "python3" ];
    instance = {
      type = "normal";
      pythonPackages = self: with self; [ beautifulsoup4 flask sqlalchemy flask-sqlalchemy tzlocal user-agent ];
      socket = "127.0.0.1:8081";
      module = "wsgi:app";
      uid = "uwsgi";
      gid = "uwsgi";
      wsgi-file = "/var/lib/behalter/wsgi.py";
      chdir = "/var/lib/behalter/";
      master = true;
      processes = 3;
      vacuum = true;
      logto = "/tmp/uwsgi.log";
    };
  };
}



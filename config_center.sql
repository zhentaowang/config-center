DROP TABLE config;
CREATE TABLE config (
  config_id int(11) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'id',
  app_name VARCHAR(30) NOT NULL COMMENT 'app name',
  config_name VARCHAR(50) NOT NULL COMMENT '配置名',
  config_content TEXT NOT NULL COMMENT '详细配置',
  version CHAR(14) NOT NULL COMMENT '版本号，年月日时分秒',
  effective TINYINT NOT NULL DEFAULT 1 COMMENT '是否有效',
  encrypt TINYINT NOT NULL DEFAULT 0 COMMENT '是否加密',
  config_owner VARCHAR(50) DEFAULT '' COMMENT '配置owner',
  created_at DATETIME DEFAULT current_timestamp COMMENT '创建时间',
  updated_at DATETIME DEFAULT current_timestamp ON UPDATE current_timestamp COMMENT '更新时间',
  PRIMARY KEY(config_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT '应用配置';

CREATE TABLE app (
  app_id int(11) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'id',
  app_name VARCHAR(30) NOT NULL COMMENT 'app name',
  secret_key VARCHAR(200) DEFAULT NULL COMMENT '应用关联的密钥',
  owner VARCHAR(50) DEFAULT '' COMMENT '应用所属',
  created_at DATETIME DEFAULT current_timestamp COMMENT '创建时间',
  updated_at DATETIME DEFAULT current_timestamp ON UPDATE current_timestamp COMMENT '更新时间',
  PRIMARY KEY(app_id),
  UNIQUE KEY uniq_app_name(app_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT '应用';
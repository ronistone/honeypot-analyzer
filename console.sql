SELECT COUNT(log_id) FROM LOGS;
SELECT COUNT(id) FROM IP;
SELECT COUNT(DISTINCT IP.IP) from IP;
SELECT COUNT(IP.IP) from IP GROUP BY IP.IP;
SELECT COUNT(id) from SUBNET;
SELECT COUNT(id) from SUBNET where IP_TYPE = 'CLOUD';


-- DELETE FROM SUBNET WHERE  IP_TYPE = 'CLOUD';
-- DELETE FROM LOGS;
-- DELETE FROM IP;
-- DELETE FROM SUBNET;


-- Quantidade de logs por ip
SELECT src_ip, LOGS_NUM from (
                                 SELECT src_ip, COUNT(src_ip) as LOGS_NUM
                                 FROM LOGS
                                 WHERE src_ip is not null
                                 GROUP BY src_ip
                             ) as GROUP_BY_IP
-- # WHERE LOGS_NUM > 2;

-- Ataques vindos da rede TOR
SELECT LOGS.* FROM LOGS, (SELECT DISTINCT IP.IP FROM IP) as IP_T WHERE LOGS.src_ip = IP_T.IP;

SELECT * FROM LOGS WHERE src_ip = '';


-- Criação da tabela dos ips relacionando com a rede tor, vpn e clouds
CREATE TABLE PROCESSED_IPS(
    id bigint auto_increment primary key,
    src_ip  varchar(100),
    IP_TYPE varchar(30),
    COUNTRY varchar(10),
    PROVIDER varchar(300),
    SRC_IP_NUM INT UNSIGNED,

	INDEX(src_ip),
	INDEX(SRC_IP_NUM)
)

SELECT
       LOGS_T.src_ip as src_ip,
       IP_QUERY.IP_TYPE as IP_TYPE,
       APP_INET_ATON(LOGS_T.src_ip) as SRC_IP_NUM
FROM
    ((SELECT LOGS_T.src_ip as 'SRC_IP', SUBNET_T.IP_TYPE as 'IP_TYPE'
            FROM (
                    SELECT LOGS.src_ip, LOGS.SRC_IP_NUM from LOGS group by src_ip, LOGS.SRC_IP_NUM
                 ) as LOGS_T, (
                    SELECT NETMASK_NUM, SUBNET_NUM, IP_TYPE FROM SUBNET group by NETMASK_NUM, SUBNET_NUM, IP_TYPE
                ) as SUBNET_T
            WHERE
    -- #               LOGS.src_ip = IP.IP
                    LOGS_T.SRC_IP_NUM IS NOT NULL
                AND (LOGS_T.SRC_IP_NUM & SUBNET_T.NETMASK_NUM) = SUBNET_T.SUBNET_NUM
        )
             union
     (
        SELECT LOG_T.src_ip as 'SRC_IP', TOR_T.IP_TYPE_TOR as 'IP_TYPE' FROM
              (
                  SELECT LOGS.src_ip from LOGS group by src_ip
              ) as LOG_T,
              (
                SELECT IP.IP, CONCAT(IP.IP_TYPE, if(IP.IS_EXIT_NODE, '-Exit-Node', '')) as IP_TYPE_TOR FROM IP group by IP.IP, CONCAT(IP.IP_TYPE, if(IP.IS_EXIT_NODE, '-Exit-Node', ''))
              ) as TOR_T
        WHERE
            LOG_T.src_ip = TOR_T.IP
     )) as IP_QUERY
        RIGHT JOIN
            (SELECT LOGS.src_ip from LOGS group by src_ip) LOGS_T
        ON IP_QUERY.SRC_IP = LOGS_T.src_ip
-- #         group by
-- #             LOGS_T.SRC_IP,
-- #             IP_QUERY.IP_TYPE
;




-- Atualizar ips processados com o país e o provider
UPDATE PROCESSED_IPS, PROVIDERS
    set PROCESSED_IPS.COUNTRY = PROVIDERS.COUNTRY,
        PROCESSED_IPS.PROVIDER = PROVIDERS.PROVIDER
    WHERE
        1=1
        and PROCESSED_IPS.src_ip is not null
        AND (PROCESSED_IPS.SRC_IP_NUM & PROVIDERS.NETMASK_NUM) = PROVIDERS.SUBNET_NUM;


-- IPs por origem clusterizada
SELECT count(src_ip), types FROM (
        SELECT count(src_ip) as 'count_ip', src_ip, GROUP_CONCAT(IP_TYPE ORDER BY IP_TYPE asc) as types FROM PROCESSED_IPS GROUP BY src_ip
    ) ips group by types;

-- IPs por origem
SELECT * FROM (
        SELECT count(src_ip) as 'count_ip', IP_TYPE FROM PROCESSED_IPS GROUP BY IP_TYPE
    ) ips;

-- Busca rede de um IP
SELECT * FROM SUBNET where
                           (INET_ATON('1.15.200.10') & INET_ATON(SUBNET.NETMASK_NUM)) = INET_ATON(SUBNET.SUBNET);

-- Match ip com subnet
SELECT PROCESSED_IPS.src_ip, PROCESSED_IPS.IP_TYPE, PROVIDERS.COUNTRY FROM PROVIDERS, PROCESSED_IPS
    WHERE 1=1
        AND (PROCESSED_IPS.SRC_IP_NUM & PROVIDERS.NETMASK_NUM) = PROVIDERS.SUBNET_NUM;

-- Limpeza de logs com prefixo ipv6
UPDATE LOGS set src_ip = TRIM(BOTH '::ffff:' FROM LOGS.src_ip) where LOGS.src_ip like '%::%';


-- Converte ipv4 para int
UPDATE SUBNET set SUBNET.SUBNET_NUM = INET_ATON(SUBNET);


-- Estatisticas de tamanho de tabelas

SELECT table_schema AS "Database",
ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS "Size (MB)"
FROM information_schema.TABLES
GROUP BY table_schema;

SELECT
     table_schema as `Database`,
     table_name AS `Table`,
     round(((data_length + index_length) / 1024 / 1024), 2) `Size in MB`
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'honeypot'
ORDER BY (data_length + index_length) DESC;

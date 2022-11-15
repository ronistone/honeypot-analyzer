SELECT COUNT(log_id) FROM LOGS;
SELECT COUNT(id) FROM IP;
SELECT COUNT(DISTINCT IP.IP) from IP;
SELECT COUNT(IP.IP) from IP GROUP BY IP.IP;



SELECT src_ip, LOGS_NUM from (
                                 SELECT src_ip, COUNT(src_ip) as LOGS_NUM
                                 FROM LOGS
                                 WHERE src_ip is not null
                                 GROUP BY src_ip
                             ) as GROUP_BY_IP
# WHERE LOGS_NUM > 2;



SELECT * FROM LOGS WHERE src_ip = '';


SELECT * FROM TOR_REPO_METADATA order by CREATED_AT desc limit 1;
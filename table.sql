


CREATE TABLE LOGS(
    log_id int NOT NULL AUTO_INCREMENT,
    arch TEXT(30000),
    compCS TEXT(30000),
	data TEXT(30000),
	destfile TEXT(30000),
	dst_ip TEXT(30000),
	dst_port int,
	duplicate BOOL,
	duration DOUBLE,
	encCS TEXT(30000),
	eventid TEXT(30000),
	fingerprint TEXT(30000),
	format TEXT(30000),
	hassh TEXT(30000),
	hasshAlgorithms TEXT(30000),
	height int,
	id int,
	input TEXT(30000),
	kexAlgs TEXT(30000),
	keyField TEXT(30000),
	keyAlgs TEXT(30000),
	langCS TEXT(30000),
	macCS TEXT(30000),
	message TEXT(30000),
	outfileField TEXT(30000),
	password TEXT(30000),
	protocol TEXT(30000),
	sensor TEXT(30000),
	session TEXT(30000),
	shasum TEXT(30000),
	size int,
	src_ip VARCHAR(100),
	src_port int,
	timestamp TEXT(30000),
	ttylog TEXT(30000),
	type TEXT(30000),
	url TEXT(30000),
	username TEXT(30000),
	version TEXT(30000),
	width int,

    PRIMARY KEY(log_id),
    INDEX(src_ip)
);

CREATE TABLE IP (
    id int AUTO_INCREMENT,
    IP varchar(50),
    IP_TYPE varchar(30),
    IS_EXIT_NODE BOOL DEFAULT TRUE,
    ENTRY_TIME datetime,
    EXIT_TIME datetime,
    IP_VERSION int,

    PRIMARY KEY(id),
    INDEX(IP),
    INDEX(ENTRY_TIME),
    INDEX(EXIT_TIME),
    INDEX(ENTRY_TIME, EXIT_TIME)
);

CREATE TABLE SUBNET (
	id int AUTO_INCREMENT,
	IP_TYPE varchar(30),
	SUBNET varchar(20),
	NETMASK varchar(20),
	ENTRY_TIME datetime,
	EXIT_TIME datetime,
	VPN_NAME varchar(200),
	IP_VERSION int,

	PRIMARY KEY(id),
	INDEX(SUBNET),
	INDEX(NETMASK),
	INDEX(SUBNET, NETMASK),
	INDEX(ENTRY_TIME),
	INDEX(EXIT_TIME)
);

CREATE TABLE TOR_REPO_METADATA(
    LAST_COMMIT_PROCESSED varchar(50) PRIMARY KEY,
	REPOSITORY_URL varchar(500),
    CREATED_AT timestamp DEFAULT CURRENT_TIMESTAMP
);
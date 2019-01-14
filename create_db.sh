DO
$do$
BEGIN
   IF EXISTS (SELECT 1 FROM pg_database WHERE datname = 'mydb') THEN
      RAISE NOTICE 'Database already exists';
   ELSE
      PERFORM dblink_exec('dbname=' || current_database()  -- current db
                        , 'CREATE DATABASE mydb');
   END IF;
END
$do$;

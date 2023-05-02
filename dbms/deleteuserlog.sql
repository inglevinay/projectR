CREATE OR REPLACE FUNCTION delete_user() RETURNS trigger AS
$$BEGIN
   insert into user_log (user_id, user_name, time, description) values (OLD.user_id, OLD.name, now(), 'Delete Account');
   RETURN OLD;
END;$$ LANGUAGE plpgsql;

CREATE TRIGGER delete_user_log
   BEFORE DELETE ON user_table FOR EACH ROW
   EXECUTE PROCEDURE delete_user(); 
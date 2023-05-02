create or replace function signup_record_trigger_fun()
returns trigger
language plpgsql
as $$
declare id_val int;
Begin
id_val := cast(nextval('user_log_log_id_seq') as int);

insert into user_log
	values(id_val,new.user_id,new.username,now(),'Sign Up');
	return new;
end;
$$;


create trigger signup_record_trigger
after insert
on user_table
for each row
execute procedure signup_record_trigger_fun();

create or replace function checklogin(inpuser varchar(20), inppass varchar(20))
returns int
as $BODY$
declare status int;
begin
if exists(select * from login where username = inpuser and password = inppass) then
	status := 0;
elsif exists(select * from login where username = inpuser) then
	status := 1;
else status := 2;
end if;
return status;

end;
$BODY$
language plpgsql;
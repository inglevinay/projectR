create or replace procedure deleteTicket (tid int)
language plpgsql 
as 
$$
declare passid int;
begin	
passid := (select pass_id from book where ticket_id = tid);
/* first delete from reserve, book, user_passenger */
delete from reserves where ticket_id = tid;
delete from book where ticket_id = tid;
delete from user_passenger where pass_id = passid;
/* then passenger and ticket */
delete from passenger where pass_id = passid;
delete from ticket where ticket_id = tid;
End;
$$;

create or replace function create_ticket(user_id_val int, train_id_val int, src_val  varchar(20), dest_val varchar(20), name_val varchar(20), age_val int, sex_val varchar(20), class_val varchar, jr_dt_val date)
returns record
language plpgsql as
$$
declare ticket_id_val int; pnr_val int; pass_id_val int; cost_val int; seat_id int; src_pos int; dest_pos int; rec record;
Begin	
	/* auto increment using max value + 1 */
	ticket_id_val := cast(nextval('ticket_serid') as int);
	pnr_val    := cast(nextval('pnr_serid') as int);
	pass_id_val:= cast(nextval('pass_serid') as int);
	
	cost_val   := calc_fare(train_id_val, class_val, src_val, dest_val);
	
	src_pos := (Select A.station_position from route A,  Station as B
		Where A.station_id = B.station_id and A.train_id = train_id_val and B.station_code = src_val);
	dest_pos := ( Select A.station_position from route A,  Station as B
		Where A.station_id = B.station_id and A.train_id = train_id_val and B.station_code = dest_val);
		
-- 	Raise notice ‘% % % % % % %’, g_tr_id, g_jr_dt, tr_cl, src_pos, dest_pos, ticket_id, pnr;
	
	seat_id := ((Select C.seat_id from Train_Coach as A,  Coach as B,  Coach_Seat as C
	Where A.coach_id = B.coach_id and B.coach_id = C.coach_id and A.train_id = train_id_val and B.class = class_val) except
	(select  X1.seat_id from reserves as A,   Ticket as B,   route as S,   route as D,   Station as S1,   Station as D1, coach_seat as X1, Coach as X
	where A.ticket_id = B.ticket_id and A.train_id = train_id_val and S.train_id = train_id_val and D.train_id = train_id_val
	and A.train_date in (select * from train_starting(train_id_val, jr_dt_val)) and S.station_id = S1.station_id and S1.station_code = B.src_station and X1.seat_id = A.seat_id and X1.coach_id = X.coach_id
	and D.station_id = D1.station_id and D1.station_code = B.dest_station
	and ( ( S. station_position < src_pos and  D. station_position > src_pos )
	or ( S. station_position < dest_pos and  D. station_position > dest_pos )
	or ( S. station_position >= src_pos and  D. station_position <= dest_pos ) )) order by seat_id limit 1);
	raise notice 'A %', seat_id;
	
	if (seat_id is NULL) then
		raise exception 'no seat available!';
		select 1, pnr_val into rec;
		return rec;
	else
		/* ticket */
		/* call ticket_procedure(ticket_id_val, pnr_val, src_val, dest_val, cost_val); */
		insert into ticket values (ticket_id_val, cost_val, src_val, dest_val, pnr_val);

		/* reservation */
-- 		Call reservation_proc(train_id_val, jr_dt_val, class_val, src_val, dest_val, ticket_id_val, pnr_val); 
		insert into reserves (train_id,train_date,seat_id,ticket_id, journey_date, pnr)
		values(train_id_val, train_starting(train_id_val, jr_dt_val), seat_id, ticket_id_val, jr_dt_val,pnr_val);
		
		/* passenger */
		/* call passenger_procedure(pass_id_val, name_val, age_val, sex_val); */
		insert into passenger values (pass_id_val, name_val, age_val, sex_val);
		
		/* User_passenger */
		insert into User_passenger values (pass_id_val, user_id_val);
		
		/* book */
		/* call book_procedure(ticket_id_val, pass_id_val); */
		insert into book values (ticket_id_val, pass_id_val);
		
		raise notice 'successfully issued ticket!';
		select 0, pnr_val into rec;
		return rec;
	end if;

end;
$$;

Select create_ticket(1, 11013, 'NGP', 'CBT', 'pooh', 69, 'T', 'AC first', cast('2023-04-12' as date));

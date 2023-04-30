create or replace function countavailableseats(tr_id int, tr_date date, src_code varchar, dest_code varchar, t_class varchar)
returns int
language plpgsql
as $$
declare src_stn_pos int; dest_stn_pos int; seat_count int;
begin

src_stn_pos := (Select A.station_position from route A,  Station as B
	Where A.station_id = B.station_id and A.train_id = tr_id and B.station_code = src_code);
dest_stn_pos := ( Select A.station_position from route A,  Station as B
	Where A.station_id = B.station_id and A.train_id = tr_id and B.station_code = dest_code);
	
seat_count := ( Select count(H.seat_id) from
((Select C.seat_id, B.coach_id, B.class from Train_Coach as A,  Coach as B,  Coach_Seat as C
Where A.coach_id = B.coach_id and B.coach_id = C.coach_id and A.train_id = tr_id) except
(select  X1.seat_id, X1.coach_id, X.class from reserves as A,   Ticket as B,   route as S,   route as D,   Station as S1,   Station as D1, coach_seat as X1, Coach as X
where A.ticket_id = B.ticket_id and A.train_id = tr_id and S.train_id = tr_id and D.train_id = tr_id
and A.train_date = tr_date and S.station_id = S1.station_id and S1.station_code = B.src_station and X1.seat_id = A.seat_id and X1.coach_id = X.coach_id
and D.station_id = D1.station_id and D1.station_code = B.dest_station
and ( ( S. station_position < src_stn_pos and  D. station_position > src_stn_pos )
or ( S. station_position < dest_stn_pos and  D. station_position > dest_stn_pos )
or ( S. station_position >= src_stn_pos and  D. station_position <= dest_stn_pos ) ))) as H group by H.class having H.class = t_class);

return seat_count;

end;$$;

select * from countavailableseats(11013, '2023-04-11', 'JIP', 'NGP', 'AC first');

create or replace function train_schedule(given_train_no int)
returns table (station_position int, day_of_week varchar, station_id int, station_name varchar, arrival_time time, departure_time time)
as $BODY$
declare status int;
begin
return query select rte.station_position, wk.dow, rte.station_id, stn.station_name, rte.arrival, rte.departure from route as rte
left join station as stn
using (station_id)
left join week as wk
on (rte.day = wk.day_no)
where train_id = 11013 order by station_position;
end;
$BODY$
language plpgsql;

select * from train_schedule(11013);
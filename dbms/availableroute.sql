CREATE OR REPLACE FUNCTION availableRoute (inputDate date, inputSrc varchar(20), inputDest varchar(20), inputclass varchar)
RETURNS TABLE (train_id int, source varchar(20), departure time, dest varchar(20), dest_arrival time, fare int, avail_seats int)
language plpgsql AS
$$
BEGIN

RETURN QUERY 
Select S.train_id,  S1.station_code as Source,  S.departure, D1.station_code as destination, D.arrival, E, seats
from route as S, route as D, Station as S1,   Station as D1, calc_fare(S.train_id, inputclass, inputSrc, inputDest) as E, countavailableseats(S.train_id, train_starting(S.train_id, inputDate), inputSrc, inputDest, inputclass) as seats
Where S.day = (select extract(dow from inputDate) )
And S.train_id = D.train_id 
And S.station_id = S1.station_id and S1.station_code = inputSrc
And D.station_id = D1.station_id and D1.station_code = inputDest
And S.station_position < D.station_position;
END;
$$;
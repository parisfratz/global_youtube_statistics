/*CREATE TABLE youtube_statistics (
    rank BIGINT,
    youtuber TEXT,
    subscribers BIGINT,
    video_views NUMERIC,
    category TEXT,
    title TEXT,
    uploads BIGINT,
    country TEXT,
    abbreviation TEXT,
    channel_type TEXT,
    video_views_rank NUMERIC,
    country_rank NUMERIC,
    channel_type_rank NUMERIC,
    video_views_for_the_last_30_days NUMERIC,
    lowest_monthly_earnings NUMERIC,
    highest_monthly_earnings NUMERIC,
    lowest_yearly_earnings NUMERIC,
    highest_yearly_earnings NUMERIC,
    subscribers_for_last_30_days NUMERIC,
    created_year NUMERIC,
    created_month TEXT,
    created_date NUMERIC,
    gross_tertiary_education_enrollment_percent NUMERIC,
    population NUMERIC,
    unemployment_rate NUMERIC,
    urban_population NUMERIC,
    latitude NUMERIC,
    longitude NUMERIC
);*/


/*
COPY hotel_bookings 
FROM 'G:\WebDesign\Data Analyst\PowerBI\Projects\hotel_bookings.csv' 
DELIMITER ',' 
CSV HEADER;*/

--select * from hotel_bookings limit 10

--SELECT COUNT(*) AS total_rows FROM hotel_bookings

/*SELECT column_name,
       data_type
FROM information_schema.columns
WHERE table_name = 'hotel_bookings'
ORDER BY ordinal_position;*/

/************ ΕΛΕΓΧΟΙ *****************/
/*Βήμα 1: Έλεγχος για κενές (NULL) τιμές -> Θέλουμε σε όλα τα πεδία το ίδιο νούμερο*/
/*SELECT 
    COUNT(*) AS total_grammes,
    COUNT(hotel) AS exoun_hotel,
    COUNT(country) AS exoun_xora,
    COUNT(adr) AS exoun_timi
FROM hotel_bookings;

SELECT COUNT(*) 
FROM youtube_statistics 
WHERE youtuber IS NULL 
   OR "rank" IS NULL 
   OR subscribers IS NULL;*/

/*Βήμα 2: Έλεγχος για διπλοεγγραφές (Duplicates) */
/*SELECT 
    hotel, arrival_date_month, arrival_date_day_of_month, lead_time, adr,
    COUNT(*) AS poses_fores_yparxei
FROM hotel_bookings
GROUP BY hotel, arrival_date_month, arrival_date_day_of_month, lead_time, adr
HAVING COUNT(*) > 1;*/

/*Βήμα 3: Έλεγχος για τρελα νουμερα (Min / Max) */
/*SELECT 
    MIN(adr) AS mikroteri_timi_domatiou,
    MAX(adr) AS megalyteri_timi_domatiou,
    MIN(adults) AS elaxistoi_enilikes,
    MAX(adults) AS megistoi_enilikes
FROM hotel_bookings;

--Με αυτό βλέπεις αμέσως το ελάχιστο και το μέγιστο. Αν π.χ. δεις κάποιο κανάλι με 0 subscribers ή αρνητικά views, 
--ξέρεις αμέσως ότι έχεις ένα «σκουπίδι» στα δεδομένα σου που θέλει διόρθωση.
SELECT MIN(subscribers), MAX(subscribers), MIN(views), MAX(views)
FROM youtube_statistics;

*/

/*Βήμα 4: Καθαρισμός Δεδομένων */
/*Στη SQL, η διαχείριση των διπλοεγγραφών θέλει προσοχή: Δεν διαγράφουμε ποτέ τυφλά γραμμές,
γιατί μπορεί να είναι απλώς δύο διαφορετικές κρατήσεις που έτυχε να έχουν ίδια στοιχεία 
(π.χ. δύο άτομα έ κλεισαν το ίδιο δωμάτιο την ίδια μέρα στην ίδια τιμή).

Ωστόσο, για να έχουμε καθαρά δεδομένα στο Power BI και να μην αλλοιώνονται τα μετρούμενα μεγέθη 
(όπως οι συνολικές κρατήσεις ή τα έσοδα), αφαιρούμε τα απόλυτα διπλότυπα (όπου όλες οι στήλες είναι ολόιδιες), 
κρατώντας κάθε φορά μόνο τη μία μοναδική εγγραφή.
Πώς καθαρίζουμε τα duplicates επαγγελματικά στην SQL;

Αντί να πειράξουμε τον αρχικό πίνακα (hotel_bookings), θα αναβαθμίσουμε το SQL View μας ώστε να φιλτράρει αυτόματα 
τα διπλότυπα χρησιμοποιώντας την εντολή DISTINCT ή ROW_NUMBER().

Ο πιο κομψός και επαγγελματικός τρόπος στη PostgreSQL είναι η χρήση του ROW_NUMBER() σε ένα CTE 
(Common Table Expression), ώστε να κρατάμε μόνο τη μία από τις διπλές εγγραφές.

Τι πετύχαμε με αυτό;

Καθαρισμός Outliers: Έφυγαν οι αρνητικές τιμές (adr < 0) και οι κρατήσεις χωρίς κανέναν επισκέπτη.
Αφαίρεση Διπλοεγγραφών: Το ROW_NUMBER() = 1 διασφαλίζει ότι αν υπάρχουν πανομοιότυπες γραμμές, 
θα περάσει στο Power BI μόνο η μία, αποτρέποντας τη διπλή μέτρηση στα έσοδα και τις κρατήσεις.

Professional Layer: Ο αρχικός πίνακας παραμένει ανέπαφος στη βάση (για auditing), 
και εμείς έχουμε ένα έτοιμο, καθαρό view (v_cleaned_hotel_bookings) αποκλειστικά για ανάλυση.*/
/*CREATE OR REPLACE VIEW v_cleaned_hotel_bookings AS
WITH ranked_bookings AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY hotel, is_canceled, lead_time, arrival_date_year, 
                            arrival_date_month, arrival_date_day_of_month, 
                            adults, children, babies, country, adr, customer_type
               ORDER BY arrival_date_year -- Κρατάμε τη μία από τις διπλές
           ) as rn
    FROM hotel_bookings
    WHERE adr >= 0 
      AND (adults + children + babies) > 0
)
SELECT 
    hotel, is_canceled, lead_time, arrival_date_year, arrival_date_month,
    arrival_date_week_number, arrival_date_day_of_month, stays_in_weekend_nights,
    stays_in_week_nights, adults, children, babies, meal, country,
    market_segment, distribution_channel, is_repeated_guest, previous_cancellations,
    previous_bookings_not_canceled, reserved_room_type, assigned_room_type,
    booking_changes, deposit_type, agent, company, days_in_waiting_list,
    customer_type, adr, required_car_parking_spaces, total_of_special_requests,
    reservation_status, reservation_status_date
FROM ranked_bookings
WHERE rn = 1;*/

/*SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
  AND table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name;*/

--select * from youtube_statistics where youtuber = 'Make Joke Of' and ctid = '(30,6)'::tid
--select * from youtube_statistics where youtuber = 'Make Joke Of'

--SELECT youtuber, COUNT(*)  FROM youtube_statistics GROUP BY youtuber
--SELECT title, COUNT(*)  FROM youtube_statistics GROUP BY title having count(*) >1

--select * from youtube_statistics where title = 'Preston'
--SELECT "rank", COUNT(*)  FROM youtube_statistics GROUP BY "rank" having count(*) >1

--SELECT MIN(subscribers), MAX(subscribers), MIN(video_views_for_the_last_30_days), MAX(video_views_for_the_last_30_days)
--FROM youtube_statistics;

SELECT * 
FROM youtube_statistics 
--WHERE subscribers <= 0 OR video_views_for_the_last_30_days <= 0;






import os
import pandas as pd

# Βρίσκει αυτόματα τον φάκελο όπου βρίσκεται το project3.py
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "global_youtube_statistics.csv")

# 1. Φόρτωση δεδομένων
# Φορτώνει το αρχείο σωστά, ανεξάρτητα από το τερματικό
df = pd.read_csv(file_path, encoding="latin-1")
total_dataset_lines = df.shape[0]
total_dataset_columns = df.shape[1]

#Το df.shape σου δίνει το μέγεθος του πίνακα (γραμμές, στήλες), οπότε το shape[0] απομονώνει καθαρά τον αριθμό των γραμμών.
print("\n----DATASET--DataFrame----")
print(f"Συνολικές γραμμές: {total_dataset_lines}, Columns: {total_dataset_columns}")

#df.columns: Παίρνει όλες τις επικεφαλίδες (τα ονόματα των στηλών) από το DataFrame σου. Από μόνο του, επιστρέφει ένα αντικείμενο τύπου Index.
#.tolist(): Μετατρέπει αυτό το Index σε μια κλασική λίστα Python (List).
print("Dataset Columns:")
print(df.columns.tolist())

#Το df.head(printed_lines) σου επιστρέφει τις πρώτες %n γραμμές σαν μια γρήγορη «προεπισκόπηση» για να τσεκάρεις ότι τα δεδομένα φόρτωσαν σωστά.
printed_lines = 5
print(f"\n--FIRST {printed_lines} LINES---")
print(df.head(printed_lines))


# 2. Καθαρισμός (Data Cleaning)
print("\n--- 2. ΕΛΕΓΧΟΣ ΓΙΑ ΔΙΠΛΟΤΥΠΑ & ΚΕΝΑ---")


# Αφαιρούμε τυχόν διπλότυπα
print("--- 2.1. ΕΛΕΓΧΟΣ ΔΙΠΛΟΤΥΠΑ ---")
print(df.isnull().sum())

duplicates = df.duplicated().sum()
print(f"Duplicated Records: {duplicates}")

current_dataset_lines = total_dataset_lines - duplicates

if duplicates > 0:
    df = df.drop_duplicates()
    print(f"\nΔιαγράφηκαν {duplicates} γραμμές μετά τον καθαρισμό διπλότυπων.\n")
    print(f"Συνολικές γραμμές στο DataFrame: {current_dataset_lines}\n")
else:
    print("No duplicates in dataset!")
  

# Καθαρίζουμε τα κείμενα από τυχόν περιττά κενά (whitespace)
#ΕΚΤΥΠΩΣΗ ΓΡΑΜΜΦΩΝ ΜΕ ΚΕΝΑ ΑΝΑ ΚΑΤΗΓΟΡΙΑ
print("--- 2.2. ΕΛΕΓΧΟΣ ΓΙΑ ΚΕΝΟΥΣ ΧΑΡΑΚΤΗΡΕΣ ---")
 
for col in df.select_dtypes(include=['object', 'str']).columns:
    original = df[col].astype(str)
    stripped = original.str.strip()
    
    mask = (original != stripped) & (original != 'nan')
    dirty_indices = df.index[mask].tolist()
    
    if dirty_indices:
        #+2 γιατι η python δεν μερταει την πρωτη γραμμη του csv που ειναι οι τιτλοι των στηλών και ξεκινάει με index 0 από τη 2η γραμμή του csv!
        print(f"\nΣτήλη '{col}': Βρέθηκαν κενά στις γραμμές {dirty_indices}+2")
        # Τυπώνουμε ακριβώς τι έγραφε πριν και τι μετά για αυτές τις γραμμές
        for idx in dirty_indices:
            print(f"  Γραμμή {idx} -> Πριν: {repr(df.loc[idx, col])} | Μετά: {repr(stripped[idx])}")
           
# Διασχίζουμε όλες τις στήλες κειμένου
counter_blank_fields = 0
text_cols = df.select_dtypes(include=['object', 'str']).columns

for col in text_cols:
    original = df[col]

    # Εντοπίζουμε τις τιμές κειμένου
    is_string = original.map(lambda x: isinstance(x, str))

    # Αφαιρούμε τα κενά από τις τιμές κειμένου
    cleaned = original.copy()
    cleaned.loc[is_string] = original.loc[is_string].str.strip()

    # Εντοπίζουμε τις τιμές που πραγματικά άλλαξαν
    changed = is_string & original.ne(cleaned).fillna(False)

    # Μετατρέπουμε τις κενές συμβολοσειρές σε pd.NA
    cleaned = cleaned.mask(cleaned.eq('').fillna(False), pd.NA)

    # Εκτυπώνουμε κάθε αλλαγή
    if changed.any():
        print(f"\nΣτήλη '{col}': Διορθώθηκαν οι παρακάτω γραμμές:")

        for idx in original.index[changed]:
            csv_line = idx + 2

            print(
                f"  -> Γραμμή CSV {csv_line} | "
                f"Πριν: {repr(original.loc[idx])} | "
                f"Μετά: {repr(cleaned.loc[idx])}"
            )
            counter_blank_fields = counter_blank_fields + 1

    df[col] = cleaned

if counter_blank_fields > 0:
    print(f"\nΟ καθαρισμός ολοκληρώθηκε και οι διορθώσεις καταγράφηκαν. Έγιναν {counter_blank_fields} διορθώσεις κενών χαρακτήρων!\n")
else:
    print("\nΟ καθαρισμός ολοκληρώθηκε και οι διορθώσεις καταγράφηκαν. Δεν χρειάστηκε καμιά διόρθωση κενών χαρακτήρων!\n")
 

#ΕΚΤΥΠΩΣΗ ΓΡΑΜΜΦΩΝ ΜΕ ΚΕΝΑ ΑΝΑ ΚΑΤΗΓΟΡΙΑ
print("--- 2.3. ΕΛΕΓΧΟΣ ΓΙΑ ΓΡΑΜΜΕΣ ΜΕ ΚΕΝΑ ΠΕΔΙΑ ---")
# Αφαίρεση εντελώς κενών γραμμών
df.dropna(how='all', inplace=True)

# Έλεγχος των ελλειπουσών τιμών
print(df.isna().sum().sort_values(ascending=False))

# ==========================================
# ΑΥΤΟΜΑΤΟΣ ΕΝΤΟΠΙΣΜΟΣ ΚΡΙΣΙΜΩΝ ΣΤΗΛΩΝ SOS -> ΘΕΛΕΙ ΠΡΟΣΩΠΙΚΟ ΕΛΕΓΧΟ ΝΑ ΚΡΙΝΩ ΠΟΙΕΣ ΣΤΗΛΕΣ ΕΙΝΑΙ ΣΗΜΑΝΤΙΚΕΣ ΚΑΙ Α ΝΕΧΟΥ ΝΚΕΝΑ ΔΕΝ ΒΟΗΘΑΝΕ ΤΑ ΣΤΑΤΙΣΤΙΚΑ ΜΟΥ, ΟΠΟΤΕ ΠΡΕΠΕΙ ΝΑ ΔΙΑΓΡΑΦΟΥΝ
# ==========================================
#------- 1ος ΕΛΕΓΧΟΣ---------#
# Βρες αυτόματα ποιες στήλες έχουν ελάχιστα έως καθόλου κενά (π.χ. < 5 κενά)
# Αυτές είναι οι στήλες-ταυτότητες (όπως το Youtuber), όχι οι μετρήσεις.
missing_counts = df.isna().sum()
auto_critical_cols = missing_counts[(missing_counts > 0) & (missing_counts < 5)].index.tolist()

print(f"\n1ος Έλεγχος: Aυτόματος εντοπισμός πιθανός κρίσιμων στηλών προς έλεγχο: {auto_critical_cols}")

#------- 2ος ΕΛΕΓΧΟΣ---------#
total_rows = len(df)

print("\n2ος Έλεγχος: Υποψήφιες στήλες ταυτοποίησης:")

for col in df.select_dtypes(include=['object', 'str']).columns:
    unique_count = df[col].nunique(dropna=True)
    missing_count = df[col].isna().sum()
    unique_ratio = unique_count / total_rows if total_rows else 0

    if unique_ratio >= 0.99:
        print(
            f"Στήλη: {col} | "
            f"Μοναδικές τιμές: {unique_count}/{total_rows} | "
            f"Κενές τιμές: {missing_count} | "
            f"Ποσοστό μοναδικότητας: {unique_ratio:.2%}"
        )

# Διαγράφουμε γραμμές ΜΟΝΟ αν λείπουν αυτές οι βασικές στήλες-ταυτότητες
CRITICAL_COLUMNS = ['Youtuber', 'Title']
if CRITICAL_COLUMNS:
    df = df.dropna(subset=CRITICAL_COLUMNS)

# Έλεγχος των ελλειπουσών τιμών μετά τον καθαρισμό
print(f"\nΓραμμές μετά τον καθαρισμό: {len(df)}\n")
print("\nΈλεγχος ελλειπουσών τιμών μετά τον καθαρισμό")
print(df.isna().sum().sort_values(ascending=False))


# 3. Εξαγωγή του καθαρού αρχείου για το Power BI
output_filename = 'cleaned_global_youtube_statistics.csv'
output_filename = os.path.join(script_dir, output_filename)
df.to_csv(output_filename, index=False, encoding='utf-8')

print(f"\nΤο καθαρό αρχείο αποθηκεύτηκε επιτυχώς ως '{output_filename}' και είναι έτοιμο για το PowerBI!\n")

# 4. Οι στήλες και οι τύποι τους για δημιουργία πίνακα στην Postegresql, ώστε να εισαχθούν ομαλά
print("#---COLUMN------------------------------------TYPE---#")
print(df.dtypes)

type_mapping = {
    'int64': 'BIGINT',
    'int32': 'INTEGER',
    'float64': 'NUMERIC',
    'float32': 'NUMERIC',
    'str': 'TEXT',
    'object': 'TEXT',
    'bool': 'BOOLEAN',
    'datetime64[ns]': 'TIMESTAMP',
}

columns_sql = []
for col, dtype in df.dtypes.items():
    sql_type = type_mapping.get(str(dtype), 'TEXT')
    
    # 1. Καθαρισμός: strip, spaces σε underscores, αφαίρεση παρένθεσεων
    # 2. Αντικατάσταση του '%' με τη λέξη 'percent' για να μην σκάει η Postgres χωρίς quotes
    # 3. Μετατροπή ΟΛΩΝ σε πεζά (.lower())
    clean_col = (
        col.strip()
        .lower()
        .replace(' ', '_')
        .replace('(', '')
        .replace(')', '')
        .replace('%', 'percent')
    )
    
    # ΧΩΡΙΣ διπλά εισαγωγικά γύρω από το clean_col πλέον!
    columns_sql.append(f'    {clean_col} {sql_type}')

create_table_query = (
    f"CREATE TABLE youtube_statistics (\n"
    + ",\n".join(columns_sql)
    + "\n);"
)

print("\nMy Postegresql Create Table Query\n\n")
print(create_table_query)

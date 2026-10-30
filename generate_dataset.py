"""
generate_dataset.py
Generates a realistic, naturally distributed synthetic passenger feedback dataset for TransitVoice.
High: Overcrowding, Cleanliness
Moderate: Delays and Punctuality, Safety and Security
Low/Long-tail: Ticketing and Fares, Staff Behaviour, Accessibility, Other Issues
"""

import pandas as pd
import os
import random

random.seed(42)

RECORDS = [
    # ── 1. Overcrowding (HIGH: 38 records) ──────────────────────────────────
    ("The bus was so packed I couldn't even board. Had to wait for the next one.", "Route 12A", "2024-10-01", "Overcrowding"),
    ("Standing room only every morning. Dangerous levels of crowding.", "Metro Line 3", "2024-10-01", "Overcrowding"),
    ("Plenty of seats available today. Very comfortable journey.", "Route 7B", "2024-10-02", "Overcrowding"),
    ("Children can't board because the bus is full of adults. Not safe.", "Route 5C", "2024-10-02", "Overcrowding"),
    ("Peak hour is unbearable. People squeezed in like sardines.", "Metro Line 2", "2024-10-03", "Overcrowding"),
    ("Not crowded at all this afternoon. Enjoyed a comfortable ride.", "Route 22", "2024-10-03", "Overcrowding"),
    ("Please add more buses during rush hour. Overcrowding is a serious problem.", "Route 9", "2024-10-04", "Overcrowding"),
    ("Couldn't get on three consecutive buses this morning. Missed an important meeting.", "Route 12A", "2024-10-04", "Overcrowding"),
    ("Good spacing today, not overly crowded. Pleasant experience.", "Route 14", "2024-10-05", "Overcrowding"),
    ("Way too many passengers for the size of the vehicle. Needs bigger buses.", "Route 18", "2024-10-05", "Overcrowding"),
    ("The train was dangerously overcrowded this evening. Someone could get hurt.", "Metro Line 1", "2024-10-06", "Overcrowding"),
    ("Nicely spaced seating and not too busy. Great journey today.", "Route 33", "2024-10-06", "Overcrowding"),
    ("Route 5C is consistently overloaded in the mornings. Need more capacity.", "Route 5C", "2024-10-07", "Overcrowding"),
    ("Please run articulated buses on this route to handle the passenger volume.", "Route 12A", "2024-10-07", "Overcrowding"),
    ("Comfortable journey with plenty of room for everyone.", "Metro Line 3", "2024-10-08", "Overcrowding"),
    ("Overcrowding makes it impossible to maintain hygiene standards on the bus.", "Route 9", "2024-10-08", "Overcrowding"),
    ("An extra service during school hours would significantly reduce crowding.", "Route 7B", "2024-10-09", "Overcrowding"),
    ("Boarded easily today. Service well managed during peak time.", "Route 22", "2024-10-09", "Overcrowding"),
    ("Standing passengers crammed into the aisle making it hard to move.", "Metro Line 2", "2024-10-10", "Overcrowding"),
    ("Off-peak travel is fine, but rush hour is chaos on this route.", "Route 18", "2024-10-10", "Overcrowding"),
    ("Bus bypassed our stop completely because it was already at maximum capacity.", "Route 12A", "2024-10-02", "Overcrowding"),
    ("Passengers were pushed against the doors. Extremely unsafe rush hour conditions.", "Metro Line 3", "2024-10-03", "Overcrowding"),
    ("Could not breathe inside the compartment. Air conditioning failed under heavy crowd.", "Metro Line 1", "2024-10-04", "Overcrowding"),
    ("We need double-decker buses on Route 5C during 8 AM to 10 AM.", "Route 5C", "2024-10-04", "Overcrowding"),
    ("People fighting to get into the metro coach due to massive overcrowding.", "Metro Line 2", "2024-10-05", "Overcrowding"),
    ("Crowd management staff needed at Central Station platform during peak evening hours.", "Central Station", "2024-10-05", "Overcrowding"),
    ("Bus was so full that passengers could not even reach the exit doors in time.", "Route 9", "2024-10-06", "Overcrowding"),
    ("The morning commute has become suffocating with extreme overcrowding.", "Route 18", "2024-10-06", "Overcrowding"),
    ("Elderly citizens cannot find seating because youth crowd every single row.", "Route 7B", "2024-10-07", "Overcrowding"),
    ("Commuters hanging near the door because the interior is completely crammed.", "Route 22", "2024-10-07", "Overcrowding"),
    ("Overcrowding at Central Station platform causes severe bottleneck at staircases.", "Central Station", "2024-10-08", "Overcrowding"),
    ("Train capacity is insufficient for the growing suburban passenger population.", "Metro Line 3", "2024-10-08", "Overcrowding"),
    ("Adding two more coaches to Metro Line 1 would resolve the daily crowding rush.", "Metro Line 1", "2024-10-09", "Overcrowding"),
    ("Seats fill up at the first stop, leaving all subsequent commuters standing.", "Route 14", "2024-10-09", "Overcrowding"),
    ("Overcrowding on rainy days gets ten times worse. Please run frequency backups.", "Route 12A", "2024-10-10", "Overcrowding"),
    ("Station concourse was overflowing with stranded passengers waiting to board.", "Central Station", "2024-10-10", "Overcrowding"),
    ("Spacious ride today with vacant seating available throughout the trip.", "Route 33", "2024-10-09", "Overcrowding"),
    ("Smooth boarding and light crowd density on the early morning express.", "Metro Line 2", "2024-10-02", "Overcrowding"),

    # ── 2. Cleanliness (HIGH: 34 records) ───────────────────────────────────
    ("The bus smelled terrible. Rubbish all over the floor.", "Route 12A", "2024-10-01", "Cleanliness"),
    ("Seats are sticky and the windows are filthy. When was this bus last cleaned?", "Route 7B", "2024-10-01", "Cleanliness"),
    ("Spotlessly clean today. Really appreciated the fresh smell.", "Metro Line 1", "2024-10-02", "Cleanliness"),
    ("Litter everywhere. This route needs daily cleaning.", "Route 5C", "2024-10-02", "Cleanliness"),
    ("Used chewing gum stuck to the seat ruined my clothes. Disgusting.", "Route 22", "2024-10-03", "Cleanliness"),
    ("Train carriage was immaculate. Very pleasant experience.", "Metro Line 3", "2024-10-03", "Cleanliness"),
    ("The toilets at the central station are absolutely revolting. Please clean them.", "Central Station", "2024-10-04", "Cleanliness"),
    ("Bus was swept and smelled clean. Great to see improved standards.", "Route 9", "2024-10-04", "Cleanliness"),
    ("Spilled drinks not cleaned up, making the floor slippery and unsafe.", "Route 14", "2024-10-05", "Cleanliness"),
    ("Graffiti on windows has not been cleaned in weeks.", "Route 18", "2024-10-05", "Cleanliness"),
    ("Very tidy bus today, seats clean and no rubbish. Well done.", "Route 33", "2024-10-06", "Cleanliness"),
    ("The station waiting area is always littered with takeaway packaging.", "Metro Line 2", "2024-10-06", "Cleanliness"),
    ("Bus clearly cleaned between runs. Smelled fresh and seats were spotless.", "Route 12A", "2024-10-07", "Cleanliness"),
    ("Mud and water tracked inside bus making everything dirty and slippery.", "Route 7B", "2024-10-07", "Cleanliness"),
    ("Clean and well-maintained vehicle. Makes the journey much more pleasant.", "Route 5C", "2024-10-08", "Cleanliness"),
    ("Windows so dirty you can't see out. Needs a proper clean urgently.", "Route 22", "2024-10-08", "Cleanliness"),
    ("Why is there always litter on Route 9? Needs daily cleaning schedule.", "Route 9", "2024-10-09", "Cleanliness"),
    ("Happy to see regular cleaning taking place. Keep it up.", "Metro Line 1", "2024-10-09", "Cleanliness"),
    ("Smells strongly of food and rubbish. Unpleasant journey.", "Route 18", "2024-10-10", "Cleanliness"),
    ("Excellent cleanliness standards maintained. Very impressed.", "Metro Line 3", "2024-10-10", "Cleanliness"),
    ("Seats are covered in thick dust and food crumbs. Unacceptable hygiene.", "Route 12A", "2024-10-02", "Cleanliness"),
    ("Disgusting stains on fabric seats. Please switch to washable vinyl seating.", "Route 5C", "2024-10-03", "Cleanliness"),
    ("Cockroaches spotted scurrying under passenger seats in coach 3.", "Metro Line 2", "2024-10-04", "Cleanliness"),
    ("Garbage bin on the platform is overflowing with plastic bottles and cups.", "Central Station", "2024-10-05", "Cleanliness"),
    ("Handrails are greasy and unsanitary. Needs regular disinfectant wiping.", "Route 7B", "2024-10-06", "Cleanliness"),
    ("The floor was sticky throughout the entire bus carriage. Needs thorough mop.", "Route 18", "2024-10-07", "Cleanliness"),
    ("Dustbins provided inside the bus were emptied regularly. Commendable hygiene.", "Route 14", "2024-10-07", "Cleanliness"),
    ("Foul sewage odor near the station underground entrance. Needs immediate sanitation.", "Metro Line 3", "2024-10-08", "Cleanliness"),
    ("Pigeon droppings on passenger waiting benches at Route 9 terminal.", "Route 9", "2024-10-08", "Cleanliness"),
    ("Carpeted floor inside airport express carriage was pristine and fresh.", "Metro Line 1", "2024-10-09", "Cleanliness"),
    ("Trash discarded under seats left uncleaned across multiple runs.", "Route 22", "2024-10-09", "Cleanliness"),
    ("Sanitizer dispenser at the bus entrance was empty for two straight weeks.", "Route 33", "2024-10-10", "Cleanliness"),
    ("Clean glass panes and vacuumed seats made for a refreshing commute.", "Route 12A", "2024-10-10", "Cleanliness"),
    ("Station restrooms were freshly disinfected and well-stocked today.", "Central Station", "2024-10-10", "Cleanliness"),

    # ── 3. Delays and Punctuality (MODERATE: 24 records) ────────────────────
    ("The bus was 25 minutes late again. I almost missed my job interview.", "Route 12A", "2024-10-01", "Delays and Punctuality"),
    ("Train delayed by 40 minutes with no announcement. Absolutely unacceptable.", "Metro Line 3", "2024-10-01", "Delays and Punctuality"),
    ("Service was on time today. Impressed!", "Route 7B", "2024-10-02", "Delays and Punctuality"),
    ("Consistent delays on the morning peak service. Happens almost every day.", "Route 5C", "2024-10-02", "Delays and Punctuality"),
    ("The schedule shown at the stop was completely wrong. Bus came 30 minutes late.", "Route 22", "2024-10-03", "Delays and Punctuality"),
    ("Punctuality has improved a lot this month. Well done.", "Metro Line 1", "2024-10-03", "Delays and Punctuality"),
    ("Running late as usual. I had to take a cab to get to work on time.", "Route 18", "2024-10-04", "Delays and Punctuality"),
    ("Three buses in a row were cancelled without warning. Left waiting 50 minutes.", "Route 9", "2024-10-04", "Delays and Punctuality"),
    ("Not a single delay this week. Very reliable service!", "Route 14", "2024-10-05", "Delays and Punctuality"),
    ("The bus arrived 15 minutes early, so I missed it. Need better schedule adherence.", "Route 33", "2024-10-05", "Delays and Punctuality"),
    ("Delays every single morning. Route 12 is notorious for this.", "Route 12A", "2024-10-06", "Delays and Punctuality"),
    ("Evening service cancelled twice this week with zero communication.", "Route 6D", "2024-10-06", "Delays and Punctuality"),
    ("On-time performance seems much better since the schedule change.", "Metro Line 2", "2024-10-07", "Delays and Punctuality"),
    ("Waited over an hour for the last bus. Had to call for a ride home.", "Route 44", "2024-10-07", "Delays and Punctuality"),
    ("The real-time tracker said 2 minutes but bus took 20. Please fix the app.", "Route 7B", "2024-10-08", "Delays and Punctuality"),
    ("Usually reliable, but today's service was 35 minutes behind schedule.", "Metro Line 1", "2024-10-08", "Delays and Punctuality"),
    ("Buses arrive bunched together and then there's a long gap. Poor scheduling.", "Route 5C", "2024-10-09", "Delays and Punctuality"),
    ("First time in months the bus was on time. Hope this continues.", "Route 22", "2024-10-09", "Delays and Punctuality"),
    ("Route 18 delayed my commute by over 45 minutes this morning.", "Route 18", "2024-10-10", "Delays and Punctuality"),
    ("Really appreciate the improved timetable. Makes planning easier.", "Route 9", "2024-10-10", "Delays and Punctuality"),
    ("Signal fault delayed Metro Line 2 for 30 minutes during morning rush.", "Metro Line 2", "2024-10-04", "Delays and Punctuality"),
    ("Bus departed 10 minutes ahead of scheduled time causing passengers to miss it.", "Route 14", "2024-10-06", "Delays and Punctuality"),
    ("Driver took an unannounced detour leading to a 20-minute journey delay.", "Route 12A", "2024-10-08", "Delays and Punctuality"),
    ("Express metro ran exactly to the minute today. Outstanding punctuality.", "Metro Line 3", "2024-10-09", "Delays and Punctuality"),

    # ── 4. Safety and Security (MODERATE: 21 records) ───────────────────────
    ("Felt very unsafe late at night. No security staff anywhere on the platform.", "Metro Line 3", "2024-10-01", "Safety and Security"),
    ("There was a group of people causing trouble and no staff intervened.", "Route 12A", "2024-10-01", "Safety and Security"),
    ("Good CCTV coverage and visible security presence. Felt safe.", "Central Station", "2024-10-02", "Safety and Security"),
    ("Emergency button on the train was broken. That is a serious safety risk.", "Metro Line 1", "2024-10-02", "Safety and Security"),
    ("Lighting at the bus stop is broken. Not safe to wait here after dark.", "Route 7B", "2024-10-03", "Safety and Security"),
    ("Well-lit stations and regular patrols. Very safe environment.", "Metro Line 2", "2024-10-03", "Safety and Security"),
    ("There was a physical altercation on the bus and the driver didn't stop.", "Route 5C", "2024-10-04", "Safety and Security"),
    ("Security staff responded quickly to a suspicious package. Reassuring.", "Central Station", "2024-10-04", "Safety and Security"),
    ("No CCTV working on this bus. Feels unsafe especially at night.", "Route 22", "2024-10-05", "Safety and Security"),
    ("Platform edge barriers are an excellent safety improvement.", "Metro Line 3", "2024-10-05", "Safety and Security"),
    ("A passenger was harassing others and no action was taken.", "Route 9", "2024-10-06", "Safety and Security"),
    ("Children travelling alone should have a designated safe waiting area.", "Route 14", "2024-10-06", "Safety and Security"),
    ("The panic alarm at the station is accessible and clearly marked. Good.", "Metro Line 1", "2024-10-07", "Safety and Security"),
    ("Dangerous driving by the bus driver put passengers at risk.", "Route 18", "2024-10-07", "Safety and Security"),
    ("Felt threatened by other passengers. Staff were not visible or helpful.", "Route 33", "2024-10-08", "Safety and Security"),
    ("Night service feels much safer since security patrols were introduced.", "Metro Line 2", "2024-10-08", "Safety and Security"),
    ("Slippery floor on the bus caused an elderly passenger to fall.", "Route 12A", "2024-10-09", "Safety and Security"),
    ("Police presence on the evening service was reassuring. Thank you.", "Route 7B", "2024-10-09", "Safety and Security"),
    ("The rear emergency exit on the bus appears to be sealed shut.", "Route 5C", "2024-10-10", "Safety and Security"),
    ("Safe, secure, and well-monitored throughout the journey. Excellent.", "Metro Line 3", "2024-10-10", "Safety and Security"),
    ("Pickpocketing incident reported at station turnstiles without any guards around.", "Central Station", "2024-10-08", "Safety and Security"),

    # ── 5. Ticketing and Fares (17 records) ─────────────────────────────────
    ("The ticket machine at the stop is broken for the third day in a row.", "Route 12A", "2024-10-01", "Ticketing and Fares"),
    ("Fare increase without any service improvement. Not happy at all.", "Metro Line 3", "2024-10-01", "Ticketing and Fares"),
    ("Mobile ticketing app worked perfectly today. Great feature.", "Route 7B", "2024-10-02", "Ticketing and Fares"),
    ("Overcharged on my contactless journey and the refund process is very slow.", "Route 5C", "2024-10-02", "Ticketing and Fares"),
    ("The weekly pass offers great value for money. Very pleased.", "Route 22", "2024-10-03", "Ticketing and Fares"),
    ("Card reader on the bus was not working. Had to pay cash instead.", "Route 9", "2024-10-03", "Ticketing and Fares"),
    ("Why has the student discount been removed? It was essential for many of us.", "Metro Line 1", "2024-10-04", "Ticketing and Fares"),
    ("Easy online ticket purchase. No queuing needed. Excellent service.", "Route 14", "2024-10-04", "Ticketing and Fares"),
    ("Was charged twice for a single journey. Still waiting for my refund.", "Route 18", "2024-10-05", "Ticketing and Fares"),
    ("Season ticket renewal process is very straightforward now. Well done.", "Metro Line 2", "2024-10-05", "Ticketing and Fares"),
    ("No change given for large notes. Machine only accepts exact fare.", "Route 33", "2024-10-06", "Ticketing and Fares"),
    ("Contactless payment works well and makes boarding faster.", "Route 12A", "2024-10-06", "Ticketing and Fares"),
    ("Got a penalty fare even though the reader failed to read my valid card.", "Metro Line 3", "2024-10-07", "Ticketing and Fares"),
    ("The new zonal pricing is confusing. Needs a clearer explanation.", "Route 7B", "2024-10-07", "Ticketing and Fares"),
    ("Ticket inspector couldn't explain why I was charged the wrong fare.", "Route 5C", "2024-10-08", "Ticketing and Fares"),
    ("Day pass great value and accepted everywhere. Very convenient.", "Route 22", "2024-10-08", "Ticketing and Fares"),
    ("Automatic fare calculation saved me money today. Smart system.", "Route 9", "2024-10-09", "Ticketing and Fares"),

    # ── 6. Staff Behaviour (14 records) ─────────────────────────────────────
    ("The driver was rude and wouldn't wait for an elderly passenger who was running.", "Route 12A", "2024-10-01", "Staff Behaviour"),
    ("Staff at the ticket office were incredibly helpful and patient.", "Central Station", "2024-10-01", "Staff Behaviour"),
    ("Driver shouted at passengers for standing near the front. Very unprofessional.", "Route 7B", "2024-10-02", "Staff Behaviour"),
    ("Friendly and cheerful driver made the whole journey enjoyable.", "Route 5C", "2024-10-02", "Staff Behaviour"),
    ("Guard refused to help a passenger with a heavy pram. Disappointed.", "Metro Line 2", "2024-10-03", "Staff Behaviour"),
    ("Driver greeted every passenger with a smile. Lovely experience.", "Route 22", "2024-10-03", "Staff Behaviour"),
    ("Driver was using his phone while driving. This is dangerous and illegal.", "Route 9", "2024-10-04", "Staff Behaviour"),
    ("The station manager sorted out my problem quickly and professionally.", "Metro Line 1", "2024-10-04", "Staff Behaviour"),
    ("Staff member was dismissive and unhelpful when I asked for directions.", "Route 14", "2024-10-05", "Staff Behaviour"),
    ("Excellent customer service from the inspector. Very impressive attitude.", "Route 18", "2024-10-05", "Staff Behaviour"),
    ("The driver drove aggressively, braking hard without warning.", "Route 33", "2024-10-06", "Staff Behaviour"),
    ("Inspector was polite and understanding when I couldn't find my ticket.", "Metro Line 3", "2024-10-06", "Staff Behaviour"),
    ("The driver waited patiently while a wheelchair user boarded. Thank you.", "Route 7B", "2024-10-07", "Staff Behaviour"),
    ("Rude staff member at the information desk. Refused to answer my question.", "Central Station", "2024-10-08", "Staff Behaviour"),

    # ── 7. Accessibility (12 records) ───────────────────────────────────────
    ("The ramp at the bus stop is broken. Wheelchair users cannot board.", "Route 12A", "2024-10-01", "Accessibility"),
    ("Audio announcements are too quiet to hear with background noise.", "Metro Line 1", "2024-10-01", "Accessibility"),
    ("The low-floor bus made boarding with my pram effortless. Thank you.", "Route 7B", "2024-10-02", "Accessibility"),
    ("No tactile paving near the platform edge. Dangerous for visually impaired.", "Metro Line 3", "2024-10-02", "Accessibility"),
    ("Step-free access was clearly signed and easy to find. Well done.", "Central Station", "2024-10-03", "Accessibility"),
    ("Priority seats were all occupied by able-bodied passengers and no one moved.", "Route 5C", "2024-10-03", "Accessibility"),
    ("Lift at the station is broken again. Third time this month.", "Metro Line 2", "2024-10-04", "Accessibility"),
    ("Staff helped me navigate the station with my walking frame. Very kind.", "Metro Line 1", "2024-10-04", "Accessibility"),
    ("No hearing loop available at ticket counter. Hard of hearing passengers struggle.", "Central Station", "2024-10-05", "Accessibility"),
    ("Large-print timetables at the stop are a brilliant idea. Very helpful.", "Route 22", "2024-10-05", "Accessibility"),
    ("Wheelchair space taken by prams with no alternative space available.", "Route 9", "2024-10-06", "Accessibility"),
    ("Station app is screen-reader compatible. Great accessibility for the visually impaired.", "Metro Line 3", "2024-10-06", "Accessibility"),

    # ── 8. Other Issues (8 records) ─────────────────────────────────────────
    ("The bus app crashes every time I open it on my phone.", "Route 12A", "2024-10-01", "Other Issues"),
    ("Journey planner website gives wrong connections. Wasted a lot of time.", "Metro Line 3", "2024-10-01", "Other Issues"),
    ("Real-time information displays at the stop are very helpful.", "Route 7B", "2024-10-02", "Other Issues"),
    ("No Wi-Fi available on the train despite it being advertised.", "Metro Line 2", "2024-10-02", "Other Issues"),
    ("Customer service phone line has an extremely long wait time.", "Route 22", "2024-10-04", "Other Issues"),
    ("USB charging port on the bus was broken and sparking. Safety hazard.", "Route 18", "2024-10-06", "Other Issues"),
    ("Air conditioning was on full blast in winter. Very uncomfortable.", "Route 33", "2024-10-06", "Other Issues"),
    ("Overall a positive experience. Service has really improved recently.", "Route 22", "2024-10-09", "Other Issues"),
]

def generate_dataset(output_path: str = "data/passenger_feedback.csv") -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = pd.DataFrame(RECORDS, columns=["feedback", "route", "date", "category"])
    df.to_csv(output_path, index=False)
    print(f"Dataset generated: {output_path} ({len(df)} records)")
    print("Category breakdown:")
    print(df["category"].value_counts())

if __name__ == "__main__":
    generate_dataset()

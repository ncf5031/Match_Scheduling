import customtkinter as ctk
from tkinter import ttk, messagebox, PhotoImage
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
from fpdf import FPDF
import json
import calendar
import tkinter as tk
from tkcalendar import Calendar


# Utility Functions
def load_data(file_name, default_data):
    try:
        with open(file_name, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return default_data

def save_data(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)

# Scraping Functions
def scrape_regional_matches(regions):
    regional_match_data = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for region in regions:
            print(f"Scraping matches for region: {region}")
            url = f"https://www.precisionrifleseries.com/profiles/clubs/{region}"
            page.goto(url)
            page.wait_for_selector("div.match-list")
            matches = page.query_selector_all("div.match-list > div.card-block.item")

            # Determine region based on URL
            match_region = "Central" if region == "CE" else "Northeast"

            for match in matches:
                date = match.query_selector("div.text-block h6").inner_text().strip()
                name = match.query_selector("div.text-block p a").inner_text().strip()
                location_element = match.query_selector("div.text-block p.meta")
                location = location_element.inner_text().strip() if location_element else "Location not provided"
                h6_html = match.query_selector("div.text-block h6").inner_html()
                qualifier = "<span>Qualifier</span>" in h6_html

                regional_match_data.append({
                    "Match Name": name,
                    "Match Date": date,
                    "Match Location": location,
                    "Qualifier": qualifier,
                    "Type": "Regional",
                    "Region": match_region  # Use the region determined from URL
                })

        browser.close()
    return regional_match_data

def scrape_national_matches():
    national_match_data = []
    with sync_playwright() as p:
        # Launch a headless browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = "https://www.precisionrifleseries.com/matches/bolt-gun/"

        # Navigate to the national matches page
        page.goto(url)

        # Wait for the match list to load
        page.wait_for_selector("table.table.table-light.table-score")

        # Select all match items within the match list
        matches = page.query_selector_all("table.table.table-light.table-score tbody tr")

        # Extract match details
        for match in matches:
            # Extract match date
            date = match.query_selector("td:nth-child(1)").inner_text().strip()

            # Extract match name
            name = match.query_selector("td:nth-child(2) a").inner_text().strip()

            # Extract match location
            location = match.query_selector("td:nth-child(3)").inner_text().strip()

            # Check if it's a qualifier
            qualifier = "QUALIFIER" in name.upper() or "QUALIFIER" in date.upper()

            # Append the extracted data to the list
            national_match_data.append({
                "Match Name": name,
                "Match Date": date,
                "Match Location": location,
                "Qualifier": qualifier,
                "Type": "National",
                "Region": ""  # Empty string for national matches
            })

        # Print the extracted data for verification
        for match in national_match_data:
            print(f"Match Name: {match['Match Name']}")
            print(f"Match Date: {match['Match Date']}")
            print(f"Match Location: {match['Match Location']}")
            print(f"Type: {match['Type']}")
            print(f"Qualifier: {'Yes' if match['Qualifier'] else 'No'}")
            print("-" * 40)

        # Close the browser
        browser.close()
    return national_match_data

# Main Application Class
class MatchSchedulerApp:
    def __init__(self):
        # Initialize data
        self.matches_file = "matches.json"
        self.work_schedule_file = "work_schedule.json"
        self.matches = load_data(self.matches_file, [])
        self.work_schedule = load_data(self.work_schedule_file, [])

        # Setup main window
        self.app = ctk.CTk()
        self.app.title("Match Scheduler")
        self.screen_width = self.app.winfo_screenwidth()
        self.screen_height = self.app.winfo_screenheight()
        x = (self.screen_width / 2) - (900 / 2)
        y = (self.screen_height / 2) - (900 / 2)
        self.app.geometry(f"900x900+{int(x)}+{int(y)}")
        self.app.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.icon = PhotoImage(file="PRS.png")
        self.app.iconphoto(False, self.icon)

        # Configure appearance
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Configure Treeview style
        self.setup_treeview_style()

        # Create tabs
        self.create_tabs()

        # Setup all tab contents
        self.setup_matches_tab()
        self.setup_work_tab()
        self.setup_calendar_tab()
        self.setup_export_tab()

    def setup_treeview_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                       background="#2a2d2e",
                       foreground="white",
                       rowheight=25,
                       fieldbackground="#343638")
        style.map("Treeview", background=[("selected", "#1f538d")])

    def create_tabs(self):
        self.tabview = ctk.CTkTabview(self.app)
        self.tabview.pack(fill="both", expand=True)

        self.matches_tab = self.tabview.add("Matches")
        self.work_tab = self.tabview.add("Work Schedule")
        self.calendar_tab = self.tabview.add("Calendar")
        self.export_tab = self.tabview.add("Export")

    def setup_matches_tab(self):
            # Create filter frame
        filter_frame = ctk.CTkFrame(self.matches_tab)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Match Type Filter (Regional/National)
        ctk.CTkLabel(filter_frame, text="Match Type:").grid(row=0, column=0, padx=5, pady=5)
        self.match_type_var = ctk.StringVar(value="All")
        self.match_type_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "Regional", "National"],
            variable=self.match_type_var,
            command=self.apply_filters
        )
        self.match_type_filter.grid(row=0, column=1, padx=5, pady=5)

        # Region Filter
        ctk.CTkLabel(filter_frame, text="Region:").grid(row=0, column=2, padx=5, pady=5)
        self.region_var = ctk.StringVar(value="All")
        self.region_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "Central", "Northeast"],
            variable=self.region_var,
            command=self.apply_filters
        )
        self.region_filter.grid(row=0, column=3, padx=5, pady=5)

        # Qualifier Filter
        ctk.CTkLabel(filter_frame, text="Qualifier:").grid(row=0, column=4, padx=5, pady=5)
        self.qualifier_var = ctk.StringVar(value="All")
        self.qualifier_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "Yes", "No"],
            variable=self.qualifier_var,
            command=self.apply_filters
        )
        self.qualifier_filter.grid(row=0, column=5, padx=5, pady=5)

        # Reset Filters Button
        reset_button = ctk.CTkButton(
            filter_frame,
            text="Reset Filters",
            command=self.reset_filters
        )
        reset_button.grid(row=0, column=6, padx=5, pady=5)

        # Create matches table
        self.matches_table = ttk.Treeview(
            self.matches_tab,
            columns=("Name", "Date", "Location", "Type", "Region", "Qualifier"),
            show="headings"
        )
        self.matches_table.heading("Name", text="Match Name")
        self.matches_table.heading("Date", text="Match Date")
        self.matches_table.heading("Location", text="Match Location")
        self.matches_table.heading("Type", text="Match Type")
        self.matches_table.heading("Region", text="Region")
        self.matches_table.heading("Qualifier", text="Qualifier")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.matches_tab, orient="vertical", command=self.matches_table.yview)
        self.matches_table.configure(yscrollcommand=scrollbar.set)

        # Pack table and scrollbar
        self.matches_table.pack(fill="both", expand=True, pady=10, padx=10)
        scrollbar.pack(side="right", fill="y")
        # Create match form
        match_form = ctk.CTkFrame(self.matches_tab)
        match_form.pack(fill="x", pady=10)

        # Match form entries
        ctk.CTkLabel(match_form, text="Match Name:").grid(row=0, column=0, padx=5, pady=5)
        self.match_name_entry = ctk.CTkEntry(match_form)
        self.match_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(match_form, text="Match Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        self.match_date_entry = ctk.CTkEntry(match_form)
        self.match_date_entry.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(match_form, text="Match Location:").grid(row=2, column=0, padx=5, pady=5)
        self.match_location_entry = ctk.CTkEntry(match_form)
        self.match_location_entry.grid(row=2, column=1, padx=5, pady=5)

        # Buttons
        add_match_button = ctk.CTkButton(match_form, text="Add Match", command=self.add_match)
        add_match_button.grid(row=3, column=0, columnspan=2, pady=10)

        scrape_regional_button = ctk.CTkButton(
            self.matches_tab,
            text="Scrape Regional Matches",
            command=self.scrape_and_update_regional_matches
        )
        scrape_regional_button.pack(pady=10)

        scrape_national_button = ctk.CTkButton(
            self.matches_tab,
            text="Scrape National Matches",
            command=self.scrape_and_update_national_matches
        )
        scrape_national_button.pack(pady=10)

        # Initialize matches table
        self.update_matches_table()

    def apply_filters(self, *args):
        """Apply all filters to the matches table"""
        self.update_matches_table()

    def reset_filters(self):
        """Reset all filters to 'All'"""
        self.match_type_var.set("All")
        self.region_var.set("All")
        self.qualifier_var.set("All")
        self.update_matches_table()

    def setup_work_tab(self):
        # Create work table
        self.work_table = ttk.Treeview(
            self.work_tab,
            columns=("Start Date", "End Date"),
            show="headings"
        )
        self.work_table.heading("Start Date", text="Start Date")
        self.work_table.heading("End Date", text="End Date")
        self.work_table.pack(fill="both", expand=True, pady=10)

        # Create work form
        work_form = ctk.CTkFrame(self.work_tab)
        work_form.pack(fill="x", pady=10)

        # Manual Work Period Fields
        ctk.CTkLabel(work_form, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5)
        self.work_start_entry = ctk.CTkEntry(work_form)
        self.work_start_entry.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(work_form, text="End Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        self.work_end_entry = ctk.CTkEntry(work_form)
        self.work_end_entry.grid(row=1, column=1, padx=5, pady=5)

        add_work_button = ctk.CTkButton(work_form, text="Add Work Period", command=self.add_work_period)
        add_work_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Rotational Schedule Fields
        ctk.CTkLabel(work_form, text="Rotational Start Date (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=5)
        self.rotational_start_entry = ctk.CTkEntry(work_form)
        self.rotational_start_entry.grid(row=3, column=1, padx=5, pady=5)

        ctk.CTkLabel(work_form, text="On Duration (weeks):").grid(row=4, column=0, padx=5, pady=5)
        self.work_on_duration_entry = ctk.CTkEntry(work_form)
        self.work_on_duration_entry.grid(row=4, column=1, padx=5, pady=5)

        ctk.CTkLabel(work_form, text="Off Duration (weeks):").grid(row=5, column=0, padx=5, pady=5)
        self.work_off_duration_entry = ctk.CTkEntry(work_form)
        self.work_off_duration_entry.grid(row=5, column=1, padx=5, pady=5)

        add_rotational_button = ctk.CTkButton(work_form, text="Add Rotational Schedule", command=self.add_rotational_schedule)
        add_rotational_button.grid(row=6, column=0, columnspan=2, pady=10)

        # Initialize work table
        self.update_work_table()

    def setup_export_tab(self):
        export_button = ctk.CTkButton(self.export_tab, text="Export to PDF", command=self.export_to_pdf)
        export_button.pack(pady=20)

    def is_duplicate_match(self, new_match):
        """Check if a match with same name and date already exists"""
        new_date = self.convert_date_format(new_match["Match Date"])
        for match in self.matches:
            existing_date = self.convert_date_format(match["Match Date"])
            if (match["Match Name"].lower() == new_match["Match Name"].lower() and
                existing_date == new_date):
                return True
        return False

    def is_past_date(self, date_str):
        """Check if a date is in the past"""
        try:
            match_date = datetime.strptime(self.convert_date_format(date_str), "%Y-%m-%d")
            return match_date.date() < datetime.now().date()
        except ValueError:
            return False

    def scrape_and_update_regional_matches(self):
        regions = ['NE', 'CE']
        try:
            new_matches = scrape_regional_matches(regions)
            matches_added = 0

            for match in new_matches:
                if self.is_past_date(match["Match Date"]):
                    continue
                if not self.is_duplicate_match(match):
                    self.matches.append(match)
                    matches_added += 1

            self.update_matches_table()
            messagebox.showinfo("Success", f"{matches_added} new regional matches added!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scrape regional matches: {str(e)}")

    def scrape_and_update_national_matches(self):
        try:
            new_matches = scrape_national_matches()
            matches_added = 0

            for match in new_matches:
                if self.is_past_date(match["Match Date"]):
                    continue
                if not self.is_duplicate_match(match):
                    self.matches.append(match)
                    matches_added += 1

            self.update_matches_table()
            messagebox.showinfo("Success", f"{matches_added} new national matches added!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scrape national matches: {str(e)}")

    def add_match(self):
        name = self.match_name_entry.get()
        date = self.match_date_entry.get()
        location = self.match_location_entry.get()

        if not name or not date or not location:
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            formatted_date = self.convert_date_format(date)

            # Check for past dates
            if self.is_past_date(formatted_date):
                messagebox.showerror("Error", "Cannot add matches from past dates!")
                return

            new_match = {
                "Match Name": name,
                "Match Date": formatted_date,
                "Match Location": location,
                "Qualifier": False
            }

            # Check for duplicates
            if self.is_duplicate_match(new_match):
                messagebox.showerror("Error", "This match already exists!")
                return

            self.matches.append(new_match)
            self.update_matches_table()

            # Clear entry fields
            self.match_name_entry.delete(0, ctk.END)
            self.match_date_entry.delete(0, ctk.END)
            self.match_location_entry.delete(0, ctk.END)
            self.update_calendar()

            messagebox.showinfo("Success", "Match added successfully!")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD.")

    def convert_date_format(self, date_str):
        """Convert various date formats to YYYY-MM-DD"""
        # Remove 'QUALIFIER' from the date string if present
        date_str = date_str.replace(" QUALIFIER", "")

        try:
            # First try the expected format
            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            try:
                # Try the "MMM DD, YYYY" format
                return datetime.strptime(date_str, "%b %d, %Y").strftime("%Y-%m-%d")
            except ValueError:
                try:
                    # Try the "MMMM DD, YYYY" format
                    return datetime.strptime(date_str, "%B %d, %Y").strftime("%Y-%m-%d")
                except ValueError:
                    print(f"Unable to parse date: {date_str}")
                    return date_str

    def update_matches_table(self):
        today = datetime.today()
        future_matches = []

        for match in self.matches:
            try:
                date_str = match["Match Date"].replace(" QUALIFIER", "")
                match_date = self.convert_date_format(date_str)

                if datetime.strptime(match_date, "%Y-%m-%d") >= today:
                    match_copy = match.copy()
                    match_copy["Match Date"] = match_date

                    # Apply filters
                    # Match Type filter
                    if self.match_type_var.get() != "All" and match_copy["Type"] != self.match_type_var.get():
                        continue

                    # Region filter - only apply to Regional matches
                    if self.region_var.get() != "All":
                        if match_copy["Type"] == "Regional" and match_copy["Region"] != self.region_var.get():
                            continue

                    # Qualifier filter
                    qualifier_status = "Yes" if match_copy.get("Qualifier", False) else "No"
                    if self.qualifier_var.get() != "All" and qualifier_status != self.qualifier_var.get():
                        continue

                    future_matches.append(match_copy)

            except ValueError as e:
                print(f"Error processing match date: {match['Match Date']} - {str(e)}")
                continue

        # Sort matches by date
        sorted_matches = sorted(
            future_matches,
            key=lambda x: datetime.strptime(x["Match Date"], "%Y-%m-%d")
        )

        # Update the table display
        self.matches_table.delete(*self.matches_table.get_children())
        for match in sorted_matches:
            qualifier_text = "Yes" if match.get("Qualifier", False) else "No"
            region_text = match["Region"] if match["Type"] == "Regional" else "N/A"
            self.matches_table.insert("", "end", values=(
                match["Match Name"],
                match["Match Date"],
                match["Match Location"],
                match["Type"],
                region_text,  # Display "N/A" for national matches
                qualifier_text
            ))

    def add_work_period(self):
        start_date = self.work_start_entry.get()
        end_date = self.work_end_entry.get()

        if not start_date or not end_date:
            messagebox.showerror("Error", "Both start and end dates are required!")
            return

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            if start_date > end_date:
                messagebox.showerror("Error", "Start date must be before end date!")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD.")
            return

        # Add the manual work period to the schedule
        self.work_schedule.append({
            "Start Date": start_date.strftime("%Y-%m-%d"),
            "End Date": end_date.strftime("%Y-%m-%d")
        })

        # Update the UI
        self.update_work_table()
        self.update_calendar()

        # Clear input fields
        self.work_start_entry.delete(0, ctk.END)
        self.work_end_entry.delete(0, ctk.END)

    def add_rotational_schedule(self):
        start_date = self.rotational_start_entry.get()
        on_duration = self.work_on_duration_entry.get()
        off_duration = self.work_off_duration_entry.get()

        if not start_date or not on_duration or not off_duration:
            messagebox.showerror("Error", "Start date, on duration, and off duration are required!")
            return

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            on_duration = int(on_duration)  # Convert "on" duration to integer (in weeks)
            off_duration = int(off_duration)  # Convert "off" duration to integer (in weeks)
        except ValueError:
            messagebox.showerror("Error", "Invalid input! Ensure dates are in YYYY-MM-DD format and durations are integers.")
            return

        # Calculate durations in days
        on_days = on_duration * 7
        off_days = off_duration * 7

        # Populate work periods until the end of the current year
        current_year = start_date.year
        end_of_year = datetime(current_year, 12, 31)
        current_date = start_date

        while current_date <= end_of_year:
            # Calculate the end date for the "on" period
            work_end_date = current_date + timedelta(days=on_days - 1)
            if work_end_date > end_of_year:
                work_end_date = end_of_year  # Ensure it doesn't go past the end of the year

            # Add the work period to the schedule
            self.work_schedule.append({
                "Start Date": current_date.strftime("%Y-%m-%d"),
                "End Date": work_end_date.strftime("%Y-%m-%d")
            })

            # Calculate the start date for the next "on" period (after the "off" period)
            current_date = work_end_date + timedelta(days=off_days + 1)

        # Update the UI
        self.update_work_table()
        self.update_calendar()

        # Clear input fields
        self.rotational_start_entry.delete(0, ctk.END)
        self.work_on_duration_entry.delete(0, ctk.END)
        self.work_off_duration_entry.delete(0, ctk.END)

    def update_work_table(self):
        self.work_table.delete(*self.work_table.get_children())
        for work in self.work_schedule:
            self.work_table.insert("", "end", values=(work["Start Date"], work["End Date"]))

    def setup_calendar_tab(self):
        # Create main calendar frame
        self.calendar_frame = ctk.CTkFrame(self.calendar_tab)
        self.calendar_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create top frame for calendar controls
        top_frame = ctk.CTkFrame(self.calendar_frame)
        top_frame.pack(fill="x", padx=5, pady=5)

        # Add month/year navigation
        self.prev_month_btn = ctk.CTkButton(top_frame, text="←", width=30, command=self.prev_month)
        self.prev_month_btn.pack(side="left", padx=5)

        self.month_label = ctk.CTkLabel(top_frame, text="")
        self.month_label.pack(side="left", padx=20)

        self.next_month_btn = ctk.CTkButton(top_frame, text="→", width=30, command=self.next_month)
        self.next_month_btn.pack(side="left", padx=5)

        # Create calendar grid
        self.calendar_grid = ctk.CTkFrame(self.calendar_frame)
        self.calendar_grid.pack(fill="both", expand=True, padx=5, pady=5)

        # Create day labels
        self.day_labels = []
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            label = ctk.CTkLabel(self.calendar_grid, text=day)
            label.grid(row=0, column=i, sticky="nsew")

        # Create day frames
        self.day_frames = []
        for row in range(6):
            for col in range(7):
                frame = ctk.CTkFrame(self.calendar_grid, fg_color="#2b2b2b")  # Dark theme color
                frame.grid(row=row+1, column=col, sticky="nsew", padx=1, pady=1)

                # Day number label
                day_label = ctk.CTkLabel(frame, text="")
                day_label.pack(anchor="nw", padx=2, pady=2)

                # Create canvas for visual indicators
                canvas = tk.Canvas(frame, height=60, highlightthickness=0, bg='#2b2b2b')  # Match dark theme
                canvas.pack(fill="both", expand=True)

                self.day_frames.append({
                    "frame": frame,
                    "label": day_label,
                    "canvas": canvas,
                    "date": None
                })

        # Configure grid weights
        for i in range(7):
            self.calendar_grid.grid_columnconfigure(i, weight=1)
        for i in range(7):
            self.calendar_grid.grid_rowconfigure(i, weight=1)

        # Create event details frame
        self.event_frame = ctk.CTkFrame(self.calendar_frame)
        self.event_frame.pack(fill="x", padx=5, pady=5)

        self.event_label = ctk.CTkLabel(self.event_frame, text="Events:")
        self.event_label.pack(anchor="w", padx=5, pady=5)

        self.event_text = ctk.CTkTextbox(self.event_frame, height=200)
        self.event_text.pack(fill="x", padx=5, pady=5)

        # Initialize calendar
        self.current_date = datetime.now()
        self.update_calendar()

    def prev_month(self):
        self.current_date = self.current_date.replace(day=1) - timedelta(days=1)
        self.update_calendar()

    def next_month(self):
        self.current_date = (self.current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
        self.update_calendar()

    def update_calendar(self):
        # Update month label
        self.month_label.configure(text=self.current_date.strftime("%B %Y"))

        # Get calendar data for current month and next month
        current_month = calendar.monthcalendar(self.current_date.year, self.current_date.month)

        # Get next month's calendar
        if self.current_date.month == 12:
            next_month = calendar.monthcalendar(self.current_date.year + 1, 1)
            next_month_year = self.current_date.year + 1
            next_month_num = 1
        else:
            next_month = calendar.monthcalendar(self.current_date.year, self.current_date.month + 1)
            next_month_year = self.current_date.year
            next_month_num = self.current_date.month + 1

        # Clear all day frames
        for day_frame in self.day_frames:
            day_frame["label"].configure(text="")
            day_frame["canvas"].delete("all")
            day_frame["date"] = None
            day_frame["frame"].configure(fg_color="#2b2b2b")
            day_frame["frame"].unbind("<Button-1>")  # Remove previous bindings

        # Fill in the calendar
        day_index = 0
        current_month_complete = False

        for week in current_month:
            for day in week:
                frame_data = self.day_frames[day_index]

                if day != 0:
                    frame_data["label"].configure(text=str(day))
                    frame_data["date"] = datetime(self.current_date.year,
                                            self.current_date.month,
                                            day)

                    # Update indicators and bind click event
                    self.update_day_indicators(frame_data)
                    frame_data["frame"].bind("<Button-1>",
                        lambda e, date=frame_data["date"]: self.show_day_events(date))

                elif current_month_complete:  # Fill with next month's dates
                    next_day = next_month[0][day_index % 7]
                    if next_day != 0:
                        frame_data["label"].configure(text=f"{next_day}")
                        frame_data["date"] = datetime(next_month_year,
                                                next_month_num,
                                                next_day)
                        frame_data["label"].configure(text_color="gray")  # Gray out next month's dates

                        # Update indicators and bind click event
                        self.update_day_indicators(frame_data)
                        frame_data["frame"].bind("<Button-1>",
                            lambda e, date=frame_data["date"]: self.show_day_events(date))

                day_index += 1
            if 0 not in week:  # If we've completed a full week
                current_month_complete = True

    def update_day_indicators(self, frame_data):
        canvas = frame_data["canvas"]
        date = frame_data["date"]

        if not date:
            return

        # Check work schedule
        for work_period in self.work_schedule:
            try:
                start = datetime.strptime(work_period["Start Date"], "%Y-%m-%d")
                end = datetime.strptime(work_period["End Date"], "%Y-%m-%d")
                if start <= date <= end:
                    # Draw blue line for work days
                    canvas.create_line(0, 30, canvas.winfo_reqwidth(), 30,
                                    fill="blue", width=4)
            except ValueError:
                continue

        # Check matches
        y_offset = 0
        colors = ["red", "green", "purple", "orange"]  # Add more colors as needed
        color_index = 0

        for match in self.matches:
            try:
                formatted_date = self.convert_date_format(match["Match Date"])
                match_date = datetime.strptime(formatted_date, "%Y-%m-%d")

                if match_date.date() == date.date():
                    # Draw colored rectangle for match
                    canvas.create_rectangle(0, y_offset, canvas.winfo_reqwidth(),
                                        y_offset + 12,
                                        fill=colors[color_index % len(colors)])
                    
                    canvas.create_text(5, y_offset + 5, anchor="w", text=match["Match Name"],
                                       fill="white", font=("Arial", 8, "bold"))
                    y_offset += 12
                    color_index += 1
            except ValueError:
                continue

    def show_day_events(self, date):
        if not date:
            return

        self.event_text.delete("1.0", tk.END)

        # Add date header
        self.event_text.insert(tk.END, f"Events for {date.strftime('%B %d, %Y')}\n\n")

        # Add work schedule information
        for work_period in self.work_schedule:
            try:
                start = datetime.strptime(work_period["Start Date"], "%Y-%m-%d")
                end = datetime.strptime(work_period["End Date"], "%Y-%m-%d")
                if start <= date <= end:
                    self.event_text.insert(tk.END, "Work Schedule\n")
                    self.event_text.insert(tk.END,
                        f"Period: {work_period['Start Date']} to {work_period['End Date']}\n\n")
            except ValueError:
                continue

        # Add match information
        matches_found = False
        for match in self.matches:
            try:
                formatted_date = self.convert_date_format(match["Match Date"])
                match_date = datetime.strptime(formatted_date, "%Y-%m-%d")

                if match_date.date() == date.date():
                    if not matches_found:
                        self.event_text.insert(tk.END, "Matches:\n")
                        matches_found = True
                    self.event_text.insert(tk.END,
                        f"- {match['Match Name']}\n  Location: {match['Match Location']}\n")
                    if match.get("Qualifier"):
                        self.event_text.insert(tk.END, "  (Qualifier)\n")
                    self.event_text.insert(tk.END, "\n")
            except ValueError:
                continue

    def export_to_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Schedule", ln=True, align="C")

        pdf.cell(200, 10, txt="Work Schedule:", ln=True)
        for work in self.work_schedule:
            pdf.cell(200, 10, txt=f"{work['Start Date']} to {work['End Date']}", ln=True)

        pdf.cell(200, 10, txt="Matches:", ln=True)
        for match in self.matches:
            pdf.cell(200, 10, txt=f"{match['Match Name']} on {match['Match Date']} at {match['Match Location']}", ln=True)

        pdf.output("schedule.pdf")
        messagebox.showinfo("Export", "Schedule exported to schedule.pdf!")

    def on_exit(self):
        save_data(self.matches_file, self.matches)
        save_data(self.work_schedule_file, self.work_schedule)
        self.app.destroy()

    def run(self):
        self.app.mainloop()

# Main execution
if __name__ == "__main__":
    app = MatchSchedulerApp()
    app.run()




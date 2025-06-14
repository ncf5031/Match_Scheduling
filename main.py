import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from fpdf import FPDF
import json
import calendar
import tkinter as tk
from tkcalendar import Calendar
import logging
import base64
import io
from PIL import Image, ImageTk
from playwright.sync_api import sync_playwright


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

ICON_DATA = """iVBORw0KGgoAAAANSUhEUgAAAPQAAAA6CAMAAACwE4QIAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAMAUExURQAAAP///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////wc9CwgAAAD/dFJOUwABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAx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
"""

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
def scrape_regional_matches(region):
    regional_match_data = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        logging.debug(f"Scraping matches for region: {region}")
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
        messagebox.showinfo("Scraping in Progress", f'Scraping matches for region: {match_region}')
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
        messagebox.showinfo("Scraping in Progress", 'Scraping national matches')
        # Print the extracted data for verification
        # for match in national_match_data:
        #     print(f"Match Name: {match['Match Name']}")
        #     print(f"Match Date: {match['Match Date']}")
        #     print(f"Match Location: {match['Match Location']}")
        #     print(f"Type: {match['Type']}")
        #     print(f"Qualifier: {'Yes' if match['Qualifier'] else 'No'}")
        #     print("-" * 40)

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
        x = (self.screen_width / 2) - (1200 / 2)
        y = (self.screen_height / 2) - (1200 / 2)
        self.app.geometry(f"1200x1200+{int(x)}+{int(y)}")
        self.app.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.icon_data = base64.b64decode(ICON_DATA)
        self.icon_image = Image.open(io.BytesIO(self.icon_data))
        self.icon = ImageTk.PhotoImage(self.icon_image)
        self.app.iconphoto(True, self.icon)

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
            show="headings",
            selectmode="extended"  # Enable multiple selection
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

        #Add delete button
        delete_button = ctk.CTkButton(match_form, text="Delete Selected Match(es)", command=self.delete_match)
        delete_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Create a frame for scrape buttons
        scrape_buttons_frame = ctk.CTkFrame(self.matches_tab)
        scrape_buttons_frame.pack(fill="x", pady=10)

        # Add "Scrape All Regions" button to the frame
        scrape_all_regions_button = ctk.CTkButton(
            scrape_buttons_frame,
            text="Update Match List With New Matches",
            command=self.scrape_and_update_regional_matches
        )
        scrape_all_regions_button.grid(row=0, column=0, padx=10, pady=10)

        # Add region-specific buttons to the frame
        scrape_northeast_button = ctk.CTkButton(
            scrape_buttons_frame,
            text="Scrape Northeast Matches",
            command=self.scrape_and_update_northeast_matches
        )
        scrape_northeast_button.grid(row=0, column=1, padx=10, pady=10)

        scrape_central_button = ctk.CTkButton(
            scrape_buttons_frame,
            text="Scrape Central Matches",
            command=self.scrape_and_update_central_matches
        )
        scrape_central_button.grid(row=0, column=2, padx=10, pady=10)

        scrape_national_button = ctk.CTkButton(
            scrape_buttons_frame,
            text="Scrape National Matches",
            command=self.scrape_and_update_national_matches
        )
        scrape_national_button.grid(row=0, column=3, padx=10, pady=10)

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

        # Add delete button for work schedule
        delete_work_button = ctk.CTkButton(work_form, text="Delete Selected Work Period", command=self.delete_work_period)
        delete_work_button.grid(row=6, column=2, columnspan=2, pady=10)

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
        
    def scrape_and_update_northeast_matches(self):
        try:
            new_matches = scrape_regional_matches('NE')
            matches_added = 0

            for match in new_matches:
                if self.is_past_date(match["Match Date"]):
                    continue
                if not self.is_duplicate_match(match):
                    self.matches.append(match)
                    matches_added += 1

            self.update_matches_table()
            save_data(self.matches_file, self.matches)
            messagebox.showinfo("Success", f"{matches_added} new Northeast matches added!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scrape Northeast matches: {str(e)}")

    def scrape_and_update_central_matches(self):
        try:
            new_matches = scrape_regional_matches('CE')
            matches_added = 0

            for match in new_matches:
                if self.is_past_date(match["Match Date"]):
                    continue
                if not self.is_duplicate_match(match):
                    self.matches.append(match)
                    matches_added += 1

            self.update_matches_table()
            save_data(self.matches_file, self.matches)
            messagebox.showinfo("Success", f"{matches_added} new Central matches added!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scrape Central matches: {str(e)}")

    def scrape_and_update_regional_matches(self):
        try:
            # Scrape both regions
            ne_matches = scrape_regional_matches('NE')
            ce_matches = scrape_regional_matches('CE')

            # Combine the results
            new_matches = ne_matches + ce_matches
            matches_added = 0

            for match in new_matches:
                if self.is_past_date(match["Match Date"]):
                    continue
                if not self.is_duplicate_match(match):
                    self.matches.append(match)
                    matches_added += 1

            self.update_matches_table()
            save_data(self.matches_file, self.matches)
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
        logging.debug("Updating matches table")
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
                logging.error(f"Error processing match date: {match['Match Date']} - {str(e)}")
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
        logging.debug("Matches table updated")

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

    def delete_work_period(self):
        selected_items = self.work_table.selection()
        if not selected_items:
            messagebox.showerror("Error", "No work period selected!")
            return

        # Confirm deletion if multiple items are selected
        if len(selected_items) > 1:
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {len(selected_items)} work periods?")
            if not confirm:
                return

        deleted_count = 0
        for selected_item in selected_items:
            work_values = self.work_table.item(selected_item, "values")
            start_date = work_values[0]
            end_date = work_values[1]

            logging.debug(f"Attempting to delete work period: {start_date} to {end_date}")

            # Count work periods before deletion
            work_periods_before = len(self.work_schedule)

            # Remove the work period
            self.work_schedule = [work for work in self.work_schedule
                        if not (work["Start Date"] == start_date and work["End Date"] == end_date)]

            # Count work periods after deletion
            work_periods_after = len(self.work_schedule)
            deleted_count += (work_periods_before - work_periods_after)

            logging.debug(f"Removed {work_periods_before - work_periods_after} work periods")

        # Save the updated work schedule to the JSON file
        save_data(self.work_schedule_file, self.work_schedule)
        logging.debug(f"Work schedule saved to file: {self.work_schedule_file}")

        # Update the work table and calendar
        self.update_work_table()
        self.update_calendar()

        if deleted_count > 0:
            if deleted_count == 1:
                messagebox.showinfo("Success", "1 work period deleted successfully!")
            else:
                messagebox.showinfo("Success", f"{deleted_count} work periods deleted successfully!")
        else:
            messagebox.showwarning("Warning", "No work periods were deleted")

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
                                        y_offset + 20,
                                        fill=colors[color_index % len(colors)])
                    
                    canvas.create_text(5, y_offset + 5, anchor="w", text=match["Match Name"],
                                       fill="white", font=("Arial", 10, "bold"))
                    y_offset += 20
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
        try:
            # Create PDF object
            pdf = FPDF(orientation='L')  # Landscape orientation for better calendar layout
            pdf.set_auto_page_break(auto=True, margin=15)

            # Get current date information
            current_year = datetime.now().year
            current_month = datetime.now().month

            # Loop through months from current month to December
            for month in range(current_month, 13):
                # Create a date object for this month
                current_date = datetime(current_year, month, 1)

                # Add a new page for each month
                pdf.add_page()
                pdf.set_font("Arial", 'B', size=16)

                # Add month title
                month_year = current_date.strftime("%B %Y")
                pdf.cell(0, 10, txt=f"Calendar - {month_year}", ln=True, align="C")
                pdf.ln(5)

                # Set up calendar grid
                pdf.set_font("Arial", 'B', size=10)
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

                # Calculate cell width (page width minus margins divided by 7 days)
                cell_width = (pdf.w - 20) / 7
                cell_height = 30

                # Draw day headers
                for i, day in enumerate(days):
                    pdf.set_fill_color(200, 200, 200)  # Light gray background
                    pdf.cell(cell_width, 10, txt=day, border=1, align="C", fill=True)
                pdf.ln()

                # Get calendar data for current month
                cal = calendar.monthcalendar(current_year, month)

                # Draw calendar cells
                pdf.set_font("Arial", size=8)

                for week in cal:
                    # Set row height
                    max_events = 0
                    for day in week:
                        if day == 0:
                            continue

                        # Count events for this day to determine cell height
                        event_count = 0
                        date = datetime(current_year, month, day)

                        # Count work periods
                        for work in self.work_schedule:
                            try:
                                start = datetime.strptime(work["Start Date"], "%Y-%m-%d")
                                end = datetime.strptime(work["End Date"], "%Y-%m-%d")
                                if start <= date <= end:
                                    event_count += 1
                            except ValueError:
                                continue

                        # Count matches
                        for match in self.matches:
                            try:
                                match_date = datetime.strptime(self.convert_date_format(match["Match Date"]), "%Y-%m-%d")
                                if match_date.date() == date.date():
                                    event_count += 1
                            except ValueError:
                                continue

                        max_events = max(max_events, event_count)

                    # Calculate row height based on events (minimum 30)
                    row_height = max(cell_height, 10 + (max_events * 5))

                    # Draw days in the week
                    for day_num in week:
                        if day_num == 0:
                            # Empty cell for days not in this month
                            pdf.cell(cell_width, row_height, txt="", border=1)
                        else:
                            # Create cell with day number
                            date = datetime(current_year, month, day_num)

                            # Start with day number
                            content = f"{day_num}\n"

                            # Add work periods
                            for work in self.work_schedule:
                                try:
                                    start = datetime.strptime(work["Start Date"], "%Y-%m-%d")
                                    end = datetime.strptime(work["End Date"], "%Y-%m-%d")
                                    if start <= date <= end:
                                        content += "WORK\n"
                                        break  # Only show once if multiple work periods
                                except ValueError:
                                    continue

                            # Add matches
                            for match in self.matches:
                                try:
                                    match_date = datetime.strptime(self.convert_date_format(match["Match Date"]), "%Y-%m-%d")
                                    if match_date.date() == date.date():
                                        # Truncate match name if too long
                                        match_name = match["Match Name"]
                                        if len(match_name) > 15:
                                            match_name = match_name[:12] + "..."  # Use ASCII ellipsis
                                        # Ensure the text is ASCII-compatible
                                        match_name = match_name.encode('ascii', 'replace').decode('ascii')
                                        content += f"{match_name}\n"
                                except ValueError:
                                    continue

                            # Ensure content is ASCII-compatible
                            content = content.encode('ascii', 'replace').decode('ascii')

                            # Draw the cell with content
                            pdf.multi_cell(cell_width, row_height/5, txt=content, border=1, align="L")
                            # Move to the right after multi_cell
                            pdf.set_xy(pdf.get_x() + cell_width, pdf.get_y() - row_height)

                    # Move to next row
                    pdf.ln(row_height)

                # Add event details section at the bottom of each month page
                pdf.ln(10)
                pdf.set_font("Arial", 'B', size=12)
                pdf.cell(0, 10, txt=f"Events for {month_year}:", ln=True)
                pdf.ln(5)

                # List matches for this month
                pdf.set_font("Arial", size=10)

                # Get matches for this month
                month_matches = []
                for match in self.matches:
                    try:
                        match_date = datetime.strptime(self.convert_date_format(match["Match Date"]), "%Y-%m-%d")
                        if match_date.month == month and match_date.year == current_year:
                            month_matches.append(match)
                    except ValueError:
                        continue

                # Sort matches by date
                month_matches.sort(key=lambda x: datetime.strptime(self.convert_date_format(x["Match Date"]), "%Y-%m-%d"))

                if month_matches:
                    for match in month_matches:
                        match_date = datetime.strptime(self.convert_date_format(match["Match Date"]), "%Y-%m-%d")
                        qualifier_text = " (Qualifier)" if match.get("Qualifier", False) else ""

                        # Ensure text is ASCII-compatible
                        match_name = match["Match Name"].encode('ascii', 'replace').decode('ascii')
                        match_location = match["Match Location"].encode('ascii', 'replace').decode('ascii')

                        pdf.cell(0, 6, txt=f"{match_date.strftime('%Y-%m-%d')}: {match_name}{qualifier_text}", ln=True)
                        pdf.cell(0, 6, txt=f"    Location: {match_location}", ln=True)
                else:
                    pdf.cell(0, 10, txt="No matches scheduled this month", ln=True)

            # Save the PDF
            pdf_filename = f"calendar_{current_year}.pdf"
            pdf.output(pdf_filename)
            messagebox.showinfo("Export", f"Calendar exported to {pdf_filename}!")

        except Exception as e:
            logging.error(f"Error exporting calendar: {str(e)}")
        messagebox.showerror("Export Error", f"Failed to export calendar: {str(e)}")

    def delete_match(self):
        selected_items = self.matches_table.selection()
        if not selected_items:
            messagebox.showerror("Error", "No matches selected!")
            return

        # Confirm deletion if multiple items are selected
        if len(selected_items) > 1:
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {len(selected_items)} matches?")
            if not confirm:
                return

        deleted_count = 0
        for selected_item in selected_items:
            match_values = self.matches_table.item(selected_item, "values")
            match_name = match_values[0]
            match_date = match_values[1]

            logging.debug(f"Attempting to delete match: {match_name} on {match_date}")

            # Count matches before deletion
            matches_before = len(self.matches)

            # Remove the match with proper date comparison
            self.matches = [match for match in self.matches
                        if not (match["Match Name"] == match_name and
                                self.convert_date_format(match["Match Date"]) == match_date)]

            # Count matches after deletion
            matches_after = len(self.matches)
            deleted_count += (matches_before - matches_after)

            logging.debug(f"Removed {matches_before - matches_after} matches")

        # Save the updated matches list to the JSON file
        save_data(self.matches_file, self.matches)
        logging.debug(f"Matches saved to file: {self.matches_file}")

        # Update the matches table and calendar
        self.update_matches_table()
        self.update_calendar()

        if deleted_count > 0:
            if deleted_count == 1:
                messagebox.showinfo("Success", "1 match deleted successfully!")
            else:
                messagebox.showinfo("Success", f"{deleted_count} matches deleted successfully!")
        else:
            messagebox.showwarning("Warning", "No matches were deleted")

    def refresh_matches_table(self):
        #logging.debug("Refreshing matches table")
        self.matches_table.delete(*self.matches_table.get_children())
        for match in self.matches:
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
        logging.debug("Matches table refreshed")

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




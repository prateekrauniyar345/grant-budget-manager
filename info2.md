## ✅ **Summary of Your Current Page**

You're building a Dash-based grant management system that:

### 1. **Collects Grant Info:**
- Grant Title
- Funding Agency
- Total Funding
- Status (Draft, Submitted, etc.)
- Start and End Dates
- Description

### 2. **Collects Personnel Info:**
- One input row for name and position (e.g., PI, Co-PI, Postdoc, etc.)
- One "Add Person" button, but **currently it does not store or render the person list**

### 3. **Collects Expense Info:**
- Staff, grad students, travel, materials, publications, tuition, and fringe rates

### 4. **Displays Auto-Calculated Fields (disabled inputs):**
- Fringe rates, indirect rate, total cost

### 5. **Includes Toast Notifications**:
- Success or failure on grant submission

### 6. **Submits Grant Data** to your backend using `Flask-Login` for authentication and a database model (`Grant`) using `SQLAlchemy`.

---

## ✅ **What Works Well**

- Clean form structure using Bootstrap.
- Smart use of `dcc.Loading` and toast notifications.
- Good separation of layout vs. callbacks.
- Secure submission logic using `current_user.is_authenticated`.

---

## 🔧 **What Needs Attention / Recommendations**

### 1. 🔁 **Personnel List Not Stored or Displayed**
You have a great input layout for personnel (PI, Co-PI, etc.) but:
- The app currently **doesn't store added people**
- There's **no DataTable or list** to show added people

#### ✅ Recommendation:
- Store added personnel in a `dcc.Store` or `dash_table.DataTable`
- Add a callback on `add-person-btn` to update the list
- You can also link it to your Excel-like design where roles are grouped under expense/fringe sections.

Would you like me to add this callback and storage logic for you?

---

### 2. 📅 **Date Handling**
You're setting `start-date` and `end-date` to today’s date by default, which is fine, but:
- You may want to validate that `end-date > start-date`

#### ✅ Recommendation:
Add validation logic in the callback to check and alert the user if the dates are invalid.

---

### 3. 🔄 **Save as Draft / Clear Buttons Not Wired Up**
These buttons exist in layout but don’t have callbacks yet.

#### ✅ Recommendation:
- Add a callback for "Clear" to reset fields (can use `dash.callback_context`)
- Add "Save as Draft" functionality (maybe store with status `"Draft"` and allow updating later)

---

### 4. ⚠️ **Static Fringe and Indirect Cost Fields**
You’re currently displaying those as disabled fields. If you plan to calculate them based on position or expense data:

#### ✅ Recommendation:
Add logic to auto-populate fringe based on selected positions (you already showed fringe % in your Excel sheet).

---

### 5. ✨ **UI Improvements (Optional)**
- Group expense inputs using collapsible `dbc.Accordion` or `dbc.Collapse` for cleaner UX.
- Display the budget summary (total personnel cost, total travel, etc.) below the form.

---

## 🔄 Next Step: Want Me to Add Personnel Tracking?

If you want, I can now:
- Add logic to collect the personnel entries (name + role) in a table
- Display them below the inputs
- Optionally allow deleting an entry before final submission































### 🧾 NIH Salary Caps and Stipends (Effective January 1, 2025)

- **Principal Investigator (PI) / Co-PI / Senior Personnel**:The NIH salary cap is set at **$225,700** per year, corresponding to Executive Level II of the federal pay scale. This cap applies to the amount of salary that can be charged to NIH grants. Institutions may pay salaries above this cap using non-federal funds citeturn0search0

- **Postdoctoral Researchers**:NIH stipends for postdoctoral fellows vary based on years of experience
  -0 years: $61,00
  -1 year: $61,42
  -2 years: $61,88
  -3 years: $64,35
  -4 years: $66,49
  -5 years: $68,96
  -6 years: $71,53
  -7 or more years: $74,08 citeturn0search0

- **Graduate Research Assistants (GRAs)**:The stipend for predoctoral trainees is **$28,224** per year citeturn0search0

- **Undergraduate Students**:The stipend for undergraduate trainees is **$14,340** per year citeturn0search2

- **Professional Staff / UI Professional Staff**:Salaries for professional staff are subject to the NIH salary cap of **$225,700** per year citeturn0search0

- **Collaborators**:Compensation for collaborators should align with their institutional salary structures and is subject to the NIH salary cap if funded by NIH grants

- **Temporary Help**:Compensation for temporary personnel should be consistent with institutional pay scales and is subject to the NIH salary cap if funded by NIH grants

---

### 📄 NSF Salary Policies

- **PI / Co-PI / Senior Personnel** NSF does not impose a specific salary cap but generally limits compensation for senior personnel to **no more than two months of their regular salary** in any one year across all NSF-funded projects. Any compensation above this limit requires NSF approval and must be justified in the proposa. citeturn0search4

- **Postdoctoral Researchers, GRAs, Undergraduates, Professional Staff, Collaborators, Temporary Help** NSF does not set fixed stipend levels for these positions. Compensation should be based on institutional salary policies and must be reasonable and allocable to the projec.

---

### 📌 Summary Tabl

| Position               | NIH Salary/Stipend           | NSF Salary Policy                                |
|------------------------|------------------------------|--------------------------------------------------|
| PI / Co-PI / Senior Personnel | Up to $225,700/year (salary cap) | Up to 2 months' salary/year across all NSF projects |
| Postdoc                | $61,008–$74,088/year (based on experience) | Institution-determined; must be reasonable and allocable |
| GRA (Predoc)           | $28,224/year                 | Institution-determined; must be reasonable and allocable |
| Undergraduate          | $14,340/year                 | Institution-determined; must be reasonable and allocable |
| Professional Staff     | Subject to $225,700/year cap | Institution-determined; must be reasonable and allocable |
| Collaborator           | Subject to $225,700/year cap | Institution-determined; must be reasonable and allocable |
| Temp Help              | Institution-determined; must be reasonable and allocable | Institution-determined; must be reasonable and allocabl |

Please note that all compensation must comply with the respective agency's policies and be justified within the grant proposal. Institutions may have additional guidelines or caps, so it's advisable to consult your institution's sponsored research office for specific budgeting practices. 
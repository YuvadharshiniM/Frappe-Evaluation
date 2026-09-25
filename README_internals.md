### B2C — Dangerous Patterns
`validate()` runs automatically during the document save process.
* **Infinite Recursion Risk:** Calling `self.save()` inside `validate()` can trigger the save process repeatedly, leading to a recursion error.
* **Unsafe Stock Updates:** Updating Spare Part stock inside `validate()` is unsafe because the method's primary role is to validate data and perform light calculations.
* **Proper Event Lifecycle:** Stock should only be reduced when the document is formally submitted, meaning stock update logic belongs in `on_submit()`.
#### Corrected Code
```python
def validate(self):
    self.total = sum(r.amount for r in self.items)
def on_submit(self):
    other = frappe.get_doc("Spare Part", self.part)
    other.stock_qty -= self.qty
    other.save()
```

### B2D — Concurrency
The **"Document has been modified after you have opened it"** error occurs when two users attempt to modify the same document simultaneously.
* **Optimistic Locking:** Frappe handles concurrency by checking the document's last modified timestamp (`modified`) before executing a save operation.
* **Conflict Detection:** If another user updates and saves the document first, Frappe detects the timestamp mismatch and blocks the second user's update.
* **Data Integrity:** This mechanism prevents users from accidentally overwriting each other's changes.

### C3 — Part Usage Entry & Service Invoice
Linked Technician Rename
No, `assigned_technician` on linked Job Cards does not update automatically.
* **Link Mechanism:** The field stores the primary key (document `name`) of the Technician record as a link.
* **Rename Behavior:** Renaming a Technician document changes its primary identifier. Existing records referencing this value will not automatically reflect the change unless Frappe's built-in document renaming handlers update foreign key dependencies properly.

### D2 — Permission Query Conditions and Safe API
The `permission_query_conditions` hook restricts **QF Technicians** to Job Cards assigned to the Technician record linked to their current Frappe user. Managers are not restricted by this condition.
* **Unsafe API (`frappe.get_all`):** Exposing `frappe.get_all()` inside a whitelisted method is dangerous because it bypasses normal permission checks and can return records that low-privilege users should not access.
* **Safe API (`frappe.get_list`):** Using `frappe.get_list()` automatically applies Frappe's permission rules, ensuring a QF Technician receives only their assigned Job Cards.
* **Field-Level Security:** The safe API strips sensitive fields (`customer_phone` and `customer_email`) from responses for non-manager users, while **QF Managers** retain access.


### E3 — Efficient Document Fetching
In the `Spare Part` `on_update` hook, use `frappe.db.get_value()` when only a single field (such as `low_stock_threshold`) is required.
* **`frappe.db.get_value()`:** Directly retrieves the required database column value, avoiding unnecessary document instantiation and keeping execution lightweight.
* **`frappe.get_doc()`:** Loads the entire `QuickFix Settings` document and creates an in-memory Document object, which is inefficient for single-field lookups. Use `get_doc()` only when invoking document methods or reading multiple fields.


### F1 — Install Seed & Wildcard Audit Log

#### Installation Seed
The `after_install` hook initializes the app environment:
* **Default Device Types Created:**
  * Smartphone
  * Laptop
  * Tablet
* **Default Settings:** Initializes `QuickFix Settings` if non-existent.
* **Notification:** Displays a success message upon completion via `frappe.msgprint()`.

#### Wildcard Audit Log
A custom **Audit Log** DocType tracks system changes using fields: `doctype_name`, `document_name`, `action`, `user`, and `timestamp`.
* **Wildcard Hook:** A wildcard `doc_events` hook catches `on_update`, `on_submit`, and `on_cancel` across documents, routing to `quickfix.audit.log_change`.
* **Recursion Guard:** The logger explicitly ignores changes to the `Audit Log` DocType itself to prevent infinite audit-creation loops.
* **Elevated Privileges (`ignore_permissions=True`):** The audit record insertion bypasses user permissions so system actions are logged reliably even if the active user lacks explicit `Create` rights on `Audit Log`.

### H1 — Client Script Async Pitfall
`frappe.call()` is an asynchronous function—it fires the HTTP request and immediately allows client-side code execution to continue before receiving the server's response.
* **Validation Timing Failure:** The client-side `validate` event runs synchronously to decide whether to permit a save action. Placing an async `frappe.call()` inside `validate` means the save workflow finishes before the server returns its response.
* **Correct Lifecycle Placement:** Asynchronous data lookups belong in early lifecycle events like `onload` or `refresh`.
* **Example Pattern:** Fetch the technician's specialization when the form loads/refreshes, cache it, and reference that cached state synchronously when fields change or during `validate`.

### J1 - Jinja Query vs. `before_print()`
Executing database calls like `frappe.get_all()` directly inside Jinja templates runs queries dynamically while the print format is rendering.
* **Performance & Maintenance Issues:** Fetching data inside Jinja can slow down print format generation and makes template code harder to debug and maintain.
* **Controller Data Fetching:** Placing the data fetching logic inside the `before_print()` hook prepares all required data on the backend prior to template execution.
* **Template Simplicity:** Fetched results can be attached directly to the document object (e.g., `doc.precomputed_field`). Jinja then simply references the prepared values, keeping the template logic clean, simple, and performant.
## TODO
- Handle hidden columns.
- generate script from model.

- For simultaneous what to do and what values to use.
- In simultaneous mode, use DO_SANS and use the time from SANS.
  - Warning if different times in SANS and TRANS. Or Gray out.
  - Use SANS times always and just do DO_SANS

- Script factory. (Different ticket)


## DONE
- pass data to save_csv method rather than QTableWidget.
- unhide columns if data in file
- load_csv should return the data array.
- Warn user if hidden column has values.
- Add units in do_trans and do_sans.
- Add options "do_trans then do_sans" and "do_sans then do_trans" in combobox.
- Move code from on_generateScriptButton_clicked to separate class (ScriptGenerator)
- Associate QTable and model. Investigate
- Add cut and copy in model.
- Bulk update.
- Update headers title from combobox.
- load and save.
- is_item_in_hidden_column needs to be updated
- Remove trailing rows but keep rows in between.

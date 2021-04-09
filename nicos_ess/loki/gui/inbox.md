## TODO
- Associate QTable and model. Investigate
- For simultaneous what to do and what values to use.
- Remove trailing rows but keep rows in between.
- In simultaneous mode, use DO_SANS and use the time from SANS.
  - Warning if different times in SANS and TRANS. Or Gray out.
  - Use SANS times always and just do DO_SANS

## DONE
- pass data to save_csv method rather than QTableWidget.
- unhide columns if data in file
- load_csv should return the data array.
- Warn user if hidden column has values.
- Add units in do_trans and do_sans.
- Add options "do_trans then do_sans" and "do_sans then do_trans" in combobox.
- Move code from on_generateScriptButton_clicked to separate class (ScriptGenerator)

# Bagrut Grade
Shows bagrut grades in a table (through [Mashov API](https://github.com/micaelillos/MashovAPI))
- high grades colored as green, low grade colored as red.
- If exam data got updated (in compare with last run), he will colored as a yellow

## Usage Examples:
```
print(mashovRequests.get_all_bagrut_data())  # all years sorted

print(mashovRequests.get_all_bagrut_data("2021, 2023"))  # 2021, 2023 grades sorted

print(mashovRequests.get_all_bagrut_data(None, False))  # all years unsorted

print(mashovRequests.get_all_bagrut_data("2021", True))  # 2021 sorted
```

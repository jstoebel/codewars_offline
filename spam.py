import os

expected_code_file = '"""\nThis has been commented out to protect from malicious code\n\n{code}\n"""\n'.format(
    code='some code'
)
print(expected_code_file)

print (os.getcwd())
with(open('kata_scrape/templates/code/python.j2', 'r')) as reader:
    print(reader.read())

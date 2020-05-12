import easyPEN

pas = easyPEN.Parser('test.epen')
pas.parse()
pas.prettify()
pas.output()
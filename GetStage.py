import LoadSheddingParser as lsp
import web

urls = '/(GetStage)', 'GetStage'

app = web.application(urls, globals())

class GetStage:
    def GET(self, name):
        print(name)
        return lsp.main()


if __name__ == "__main__":
    app.run()
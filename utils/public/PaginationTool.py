from rest_framework.pagination import PageNumberPagination


class PageNum(PageNumberPagination):
    """
    自定义分页器
    """

    page_size_query_param = 'page_size'
    '指定控制每页数量的参数'

    page_size = 12
    '每页返回数量'

    max_page_size = 20
    '指定每页最大返回数量'

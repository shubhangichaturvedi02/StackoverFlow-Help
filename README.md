# StackoverFlow-Help

An application built over StackOverflowAPI for searching questions in StackOverflow (ref: https://api.stackexchange.com/docs/advanced-search) using django framework.


Features:
1) It is able to search all available fields/parameters. 
2) Listing the result with pagination.
3) Page/Data has been be cached using REDIS. (Application only calls StackOverflowAPI if we didn't pull data already for same query param)
4) Search limit per min(5) and per day(100) for each session.

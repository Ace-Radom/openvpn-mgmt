bind = "127.0.0.1:9532"
workers = 2
forwarded_allow_ips = "*"

accesslog = "-"
access_log_format = '%({X-Forwarded-For}i)s:%({X-Client-Port}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s'

errorlog = "-" 

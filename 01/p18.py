def equal(x):
    s=str(x)
    for i in range(len(s)):
        if s[i]==s[len(s)-i-1]:
            continue
        else:
            return False
    return True

output=filter(equal,range(1,1000))
print("1-1000:",list(output))


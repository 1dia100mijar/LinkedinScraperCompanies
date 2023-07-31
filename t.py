def main():
    a = {}

    for i in range (5):
        a[i] = "a"+str(i)
    
    for aux, a in a.items():
        print(aux,a)

if __name__ == "__main__":
    main()
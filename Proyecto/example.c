// Type your code here, or load an example.
int A[10];

int Ackerman(int m, int n){
    if (m==0){ 
        return n + 1; 
    } 
    else{
        if (n==0){
            return Ackerman(m - 1, 1);
        }
        else{
            return Ackerman(m-1, Ackerman(m,n-1));
        }
    }
}

void OutputInt(int n){
}

int InputInt(void){
    return 0;
}

int main(){
    int i;
    int j;
    i = 0;
    j=0;
    
    while(i<10){
        A[i]=InputInt();
        i = i+1;
    }
    i=0;
    while (i<10){
        OutputInt(Ackerman(A[i],j));
        i = i+1;
    }
}

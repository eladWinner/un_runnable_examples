public class list<T> {
    linkedList<T> first=null , current = null , last = null;
    // int size =0; // dont need / want
    public list(linkedList<T> l ){first=l; current=l;last=l;}
    public T currentValue(){if (current!=null) return current.value; return null;}
    public void addtoStart( linkedList<T> ll){
        if (current == first)
            current=ll;
        first=first.setprev(ll);
    }
    public void addtoStart( T val){this.addtoStart(new linkedList<>(val));}
    public boolean isAtEnd(){return current==last;}
    public void addtoEnd (linkedList<T> ll){
        if (first==null)
            addtoStart(ll);
        else
            last=last.setnext(ll).next;
    }
    public void removecurrent (){
        if (last == current)
            last=current.prev;
        if ( first== current)
            first= current.next;
        current=current.removeself();
    }
    public boolean goNext(){if (current!=last) {current=current.next; return  true;}return false;}
    public void goNext(int times){ while (times >0){ times--; this.goNext();}}
    public void addListToEnd ( list<T> otherL){
        if (otherL !=null) {this.addtoEnd(otherL.first);last=otherL.last;}
    }
    public int length(){ int count =1; linkedList<T> temp =first ; while (temp!=last){count++;temp=temp.next; }return count;}
    public void push(linkedList<T> ll ){this.addtoStart(ll);}
    public linkedList<T> pop(){
        linkedList<T> temp =first;
        if (current == first)
            current=first.next;
        first =first.removeself();
        temp.next =null ; temp.prev=null;
        return temp;
    }
    public void flip(){
        // i dont want to do this
        if (first!=last) // above length
        {
            linkedList<T> orignalLast =last;
            last =first;
            if (first.next!=last)// above length of 2
            {
                linkedList<T> twoahead = first.next.next;
                while (twoahead!=null){
                    //twoahead.prev is the next in flipping  ( with first )
                    first.prev=twoahead.prev; // changing order
                    twoahead.prev.next=first;
                    twoahead=twoahead.next; // two is still uneffected
                    first=first.prev; // order was flipped
                }
                // at this point there are  2 last links are unflipped
                // at thies point first is point at the orignally 2nd last link
            }
            first.prev=orignalLast;
            orignalLast.next=first;
            first=orignalLast;
            //cut lose ends
            first.prev= null;
            last.next=null;
        }
    }
    public void print(){
        linkedList<T> at =first;
        boolean atlast =false;
        while (!atlast){
            System.out.print(at.value+", ");
            atlast = at ==last;
            at=at.next;
        }
    }

}


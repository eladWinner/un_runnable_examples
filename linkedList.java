public class linkedList<T> {
    public T value;
    public linkedList<T> next = null,prev = null ;

    public linkedList (T v){value=v;}
    public linkedList<T> addnext( T v){next=new linkedList<>(v); next.prev = this; return this;}
    public linkedList<T> setnext(linkedList<T> other){next=other; other.prev=this; return  this;}
    public linkedList<T> addprev( T v){prev=new linkedList<>(v); prev.next= this; return prev;}
    public linkedList<T> setprev(linkedList<T> other){prev=other; other.next=this; return  other;}
    public linkedList<T> removeself(){
        if ( prev!=null){
            prev.next=next;//skipp my self
            return prev;}
        return next; // if no next it returns null ;
    }
}

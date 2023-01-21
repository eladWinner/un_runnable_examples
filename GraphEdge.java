public class GraphEdge {
    public GraphNode from;
    public GraphNode to;
    public GraphEdge otherDiraction; //one copy of edge belongs to FROM while other belongs to TO
    private boolean belongsToFrom =true;
    public GraphEdge next =null,previous=null;
    public GraphEdge(GraphNode from1, GraphNode to1 ) {
        from =from1 ;to = to1;
        otherDiraction= new GraphEdge(from1,to1,this);
        if(from.adjout==null)
            next=null;
        else
            next=from.adjout;
        if(from.adjout!=null)
            from.adjout.previous= this;
        from.adjout=this;
    }
    private GraphEdge(GraphNode from1, GraphNode to1 ,GraphEdge otherDiraction1 ) {
        belongsToFrom=false;from =from1 ;to = to1;
        otherDiraction=otherDiraction1;
        //doesnt belong to from
        if(from.adjout==null)
            next=null;
        else
            next=to.adjin;
        if(to.adjin!=null)
            to.adjin.previous=this;
        to.adjin=this;
    }

    public void removemyself()
    {
        if (previous!=null)
            previous.next=next; // skipping it self
        else
            {
                if (belongsToFrom)
                    from.adjout =from.adjout.next ; // skips it self , if next is null its ok
                else
                    to.adjin =to.adjin.next ;
            }
    }
    public void removeEdge(){
        this.removemyself();
        otherDiraction.removemyself();
    }

    public GraphEdge(GraphNode from1, GraphNode to1 ,boolean iKnowWhatImDoing ) { //used for wierd list none list ?!?
        from =from1 ;to = to1; }
}

//@author: Jonas Schlund
pragma solidity ^0.4.18;

contract CommunityController_v13 {
    
	//addresses
	address public owner;
    
	//mappings
	mapping(address => bool) public registered; //true if address is registered
    mapping(address => uint) private SOC; //currrent SOC of address 
    mapping(address => int) private Pres; //current Pres of address (Consumer counting arrow system)
	mapping(address => uint) private PoptCh; //optimal charging operatopn point of address
	mapping(address => uint) private PoptDch; //optimal discharging operation point of address
	mapping(uint => address) public RegisteredAddresses;  //address of registered index 
	mapping(address => uint) public RegistrationIndex;  //index of registered address
	mapping(address => int) public active; //counter for activeness
	
	//other
	uint public numberOfAdresses=0; //total number of registered addresses
    
	//modifiers
    modifier onlyOwner()
    {
        require(msg.sender == owner);
        _;
    }
    
    modifier onlyRegistered()
    {
        require(registered[msg.sender] == true);
        _;
    }
	
	modifier onlyNonregistered()
	{
        require(registered[msg.sender] == false);
        _;
    }
	
	//constructor
	function CommunityController_v13() public 
    {
        owner = msg.sender;
		//register(); //register owner 
    }
	
	//registration/deregistration
	function register(uint PoptCh_i, uint PoptDch_i) public onlyNonregistered
	{
		registered[msg.sender] = true;
		RegisteredAddresses[numberOfAdresses]=msg.sender;
		RegistrationIndex[msg.sender]=numberOfAdresses++;
		setPoptCh(PoptCh_i);
		setPoptDch(PoptDch_i);
		active[msg.sender] = 13;
	}
	
	function deregister() public onlyRegistered
	{
		registered[msg.sender] = false;
		SOC[msg.sender]=0;
		Pres[msg.sender]=0;
		PoptCh[msg.sender]=0;
		PoptDch[msg.sender]=0;
		RegisteredAddresses[RegistrationIndex[msg.sender]]=RegisteredAddresses[numberOfAdresses-1];
		RegistrationIndex[RegisteredAddresses[numberOfAdresses-1]]=RegistrationIndex[msg.sender];
		RegisteredAddresses[numberOfAdresses-1]=0;
		RegistrationIndex[msg.sender]=0;
		numberOfAdresses--;
		active[msg.sender] = 0;
	}
	
	function deregister(address _a) internal 
	{
	    registered[_a] = false;
		SOC[_a]=0;
		Pres[_a]=0;
		PoptCh[_a]=0;
		PoptDch[_a]=0;
		RegisteredAddresses[RegistrationIndex[_a]]=RegisteredAddresses[numberOfAdresses-1];
		RegistrationIndex[RegisteredAddresses[numberOfAdresses-1]]=RegistrationIndex[_a];
		RegisteredAddresses[numberOfAdresses-1]=0;
		RegistrationIndex[_a]=0;
		numberOfAdresses--;
		active[_a] = 0;
	}
	
	//automatic recognation of offline neighbors
	function checkNeighbors() internal 
	{
        if (numberOfAdresses==1)
        {}
        else
        {
                int n = int(RegistrationIndex[msg.sender])-1;
                if (n == -1)
                {
                    n=int(numberOfAdresses)-1;
                }
                uint m = RegistrationIndex[msg.sender]+1;
                if (m == numberOfAdresses)
                {
                    m=0;
                }
                if(--active[RegisteredAddresses[uint(n)]]<0)
                {
                    deregister(RegisteredAddresses[uint(n)]);
                }
                if(--active[RegisteredAddresses[m]]<0)
                {
                    deregister(RegisteredAddresses[uint(m)]);
                }
        }
	}
	
	//setters
    function setSOC(uint _newvalue) public onlyRegistered
    {
        SOC[msg.sender] = _newvalue;
        active[msg.sender] = 9;
        checkNeighbors();
    }
    
    function setPres(int _newvalue) public onlyRegistered //Consumer counting arrow system
    {
        Pres[msg.sender] = _newvalue;
    }
	
	function setPoptCh(uint _newvalue) public onlyRegistered //only at registration / if updated
    {
        PoptCh[msg.sender] = _newvalue;
    }
	
	function setPoptDch(uint _newvalue) public onlyRegistered //only at registration / if updated
    {
        PoptDch[msg.sender] = _newvalue;
    }
    
	//getters
    function readSOC(address _a) public onlyRegistered view returns (uint) 
    {
        return SOC[_a];
    }
	
	function readPres(address _a) public onlyRegistered view returns (int) 
    {
        return Pres[_a];
    }
	
	function readInstruction() public onlyRegistered view returns (int)
	{
		return readInstruction(msg.sender);
	}
	
	function readInstruction(address _a) internal view returns (int) 
	{
		//get total residual load of community
		int PresTotal = 0;
		for (uint i=0;i<numberOfAdresses;i++)
		{
			PresTotal+=Pres[RegisteredAddresses[i]];
		}
		
		//instruction for _a
		int returnValue=0;

        //counter of optimal operation points of active ESSs
		uint PoptTotal = 0;
		
		//sort depending on SOC
		uint[] memory Order = new uint[](numberOfAdresses);
		uint[] memory Pos = new uint[](numberOfAdresses);
		for (i=0;i<numberOfAdresses;i++)
		{
			Pos[i]=SOC[RegisteredAddresses[i]];
		}
		Pos = getPos(Pos);
        Order=getOrder(Pos);	
		
		//index of last active ESS 
		uint LastOne = Order[numberOfAdresses-1];
		
		//start allocation of power
		//case 1: positive residual load --> discharge ESSs
		if (PresTotal>0)
		{
			for (i=0;i<numberOfAdresses;i++)
			{   
			    //add up optimal operation points for charging from high to low SOC
				PoptTotal += PoptDch[RegisteredAddresses[Order[i]]];
				
				//stop if total residial load is reached
				if (PoptTotal >= uint(PresTotal))
				{
					//choose the index which is closer 
					if ((PoptTotal-PoptDch[RegisteredAddresses[Order[i]]])/2<uint(PresTotal)||i==0)
					{
					    //i is closest
					    LastOne=Order[i];
					}
					else
					{
					    //i-1 is closest
					    LastOne=Order[i-1];
					    PoptTotal-=PoptDch[RegisteredAddresses[Order[i]]];
					}
					break;
				}
			}
			if (LastOne==Order[numberOfAdresses-1])
			{
			    //all ESSs are active --> use adapted optimal operation points
				returnValue = int(PoptDch[_a]*uint(PresTotal)/PoptTotal);
			}
			else
			{
			    //only parts are active
			if (Pos[RegistrationIndex[_a]]<=Pos[LastOne])//(SOC[_a]>SOC[RegisteredAddresses[LastOne]]||_a==RegisteredAddresses[LastOne])
				{
				    //_a active
					returnValue = int(PoptDch[_a]*uint(PresTotal)/PoptTotal);
				}
				else
				{
				    //_a inactive
					returnValue = 0;
				}
			}
		}
		//case 2: no residial load --> nothing to do
		else if (PresTotal==0)
		{
			returnValue = 0;
		}	
		//case 3: negative load --> charge 
		else
		{
			//index of last active ESS 
			LastOne=Order[0];
			for (i=0;i<numberOfAdresses;i++)
			{
			    //add up optimal charging points from low to high SOC
				PoptTotal += PoptCh[RegisteredAddresses[Order[numberOfAdresses-1-i]]];
				
				//stop if total residial load is reached
				if (PoptTotal >= uint(-PresTotal))
				{
					//choose the index which is closer 
					if ((PoptTotal-PoptCh[RegisteredAddresses[Order[numberOfAdresses-1-i]]])/2<uint(-PresTotal)||i==0)
					{
					    //i is closest
					    LastOne=Order[numberOfAdresses-1-i];
					}
					else
					{
					    //i-1 is closest
					    LastOne=Order[numberOfAdresses-i];
					    PoptTotal-=PoptCh[RegisteredAddresses[Order[numberOfAdresses-1-i]]];
					}
					break;
				}
			}
			if (LastOne==Order[0])
			{
			    //all ESSs are active --> use adapted optimal operation points
				returnValue = -int(PoptCh[_a]*uint(-PresTotal)/PoptTotal); //todo add charging / discharging missing maximum/minimum!!
			}
			else
			{
			    //only parts are active
				if (Pos[RegistrationIndex[_a]]>=Pos[LastOne])//(SOC[_a]<SOC[RegisteredAddresses[LastOne]]||_a==RegisteredAddresses[LastOne]) //(LastOne>=RegistrationIndex[_a])//todo zero or close to Popt depending on index
				{
					//_a active
					returnValue = -int(PoptCh[_a]*uint(-PresTotal)/PoptTotal);
				}
				else
				{
				    //_a inactive 
					returnValue = 0;
				}
			}
		}
		return returnValue;
	}
	
	function getPos(uint[] memory data) public pure returns (uint[] memory) {

		uint n = data.length;
		uint[] memory arr = new uint[](n);
		uint i;
		uint j;

		for(i=0; i<n; i++) {
		  arr[i] = 0;
		  for(j=0; j<n; j++)
		  {
			  if(data[i]<data[j]||(data[i]==data[j]&&j<i))
			  {
				  arr[i]++;
			  }
		  }
		}
		return arr;
	}
	function getOrder(uint[] memory data) internal pure returns (uint[] memory) {
	  
		uint n = data.length;
		uint[] memory arr = new uint[](n);
		//uint[] memory temp = new uint[](n);
		uint i;
		uint j;
		//temp = getPos(data);
		for(i=0; i<n; i++)
		{  
			for(j=0; j<n; j++)
			{
				if(i==data[j])
				{
						arr[i] = j;
				}
			}
		}
		return arr;
	}

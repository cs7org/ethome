"""
@author: Jonas Schlund
simple battery model based on [1]
exact parameterization is property of Siemens AG and therefore not published
"""
import math
class battery(object):
	def __init__(self, Emax, Pmax_ch, Pmax_dch, Estart):		
		#general variables
		self.E = Estart * 1000000 * 3600 #kWh --> mWs
		self.Emax = Emax * 1000000 * 3600 #kWh --> mWs
		self.Pmax_ch = Pmax_ch * 1000000 #kW --> mW 
		self.Pmax_ch_id = Pmax_ch * 1000000 #kW --> mW
		self.Pmax_dch = Pmax_dch * 1000000 #kW --> mW 
		
		#variables for losses statistics
		self.Elosses_charge = 0
		self.Elosses_discharge = 0
		self.Elosses_idle_internal = 0
		self.Elosses_idle_external = 0
		
		#idle parameters
		self.lossesIdle = 15000 #mW
		
		#Inverter parameters (TODO: fit according to [1])
		self.ac = 
		self.bc = 
		self.cc = 
		self.ad = 
		self.bd = 
		self.cd = 
		
		#Battery parameters (fitted according to [1])
		self.t = 0.9975
		self.m = -0.04488
		
	def charge(self,P,t):
		Pint = min (-P, self.Pmax_ch)
		z = Pint/float(self.Pmax_ch_id)
		x = z * 3000
		eff = (self.ac * x / (self.bc + x) + self.cc * x)/100 * math.sqrt(z*self.m+self.t)
		if self.Emax-self.E >= int(Pint*t*eff):
			self.E+=int(Pint*t*eff)
			self.Elosses_charge+=int(Pint*t*(1-eff))
			self.updateLimits()
			return -Pint
		else:
			return self.idle(t)
	def discharge(self,P,t):
		Pint = min (P, self.Pmax_dch)
		z = Pint/float(self.Pmax_dch)
		x = z * 3000 
		eff = (self.ad * x / (self.bd + x) + self.cd * x)/100 * math.sqrt(z*self.m+self.t)
		if self.E>=int(Pint*t/eff):
			self.E-=int(Pint*t/eff)
			self.Elosses_discharge+=int(Pint*t*(1/eff-1))
			self.updateLimits()
			return Pint
		else:
			return self.idle(t)
	def idle(self,t):
		self.updateLimits()
		if self.E>=self.lossesIdle*t:
			self.E-=self.lossesIdle*t
			self.Elosses_idle_internal+=self.lossesIdle*t
			return 0
		else:
			self.Elosses_idle_external+=self.lossesIdle*t
			return -self.lossesIdle*t
	def updateLimits(self):
		if(self.E<0.9*self.Emax):
			self.Pmax_ch=self.Pmax_ch_id
		else:
			self.Pmax_ch=self.Pmax_ch_id*(1-6.7*(self.E/self.Emax-0.9))
	def SOC(self):
		return int(self.E*100000/self.Emax) #in m%
	def E_losses_charge(self):
		return self.Elosses_charge
	def E_losses_discharge(self):
		return self.Elosses_discharge
	def E_losses_idle_internal(self):
		return self.Elosses_idle_internal
	def E_losses_idle_external(self):
		return self.Elosses_idle_external
	def Popt_charge(self):
		return int(self.Pmax_ch_id/2)
	def Popt_discharge(self):
		return int(self.Pmax_dch/2)
	def __del__(self):
		pass
"""
[1] https://www.researchgate.net/publication/319351878_Investigation_modeling_and_simulation_of_redox-flow_lithium-ion_and_lead-acid_battery_systems_for_home_storage_applications
"""

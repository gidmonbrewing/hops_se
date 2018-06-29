# encoding: utf-8
from django.db import models
from noctoz_common.models import ContentStreamItem
#from django_facebook.models import FacebookProfileModel
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.forms import ModelForm
from decimal import *

class Region(models.Model):
	name = models.CharField(max_length=50)

	def __unicode__(self):
		return self.name

class Country(models.Model):
	name = models.CharField(max_length=50)
	region = models.ForeignKey(Region)
	
	def __unicode__(self):
		return self.name

class Town(models.Model):
	name = models.CharField(max_length=50)
	country = models.ForeignKey(Country)
	
	def __unicode__(self):
		return self.name

class TownForm(ModelForm):
	class Meta:
		model = Town

class Brewery(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True, null=True)
	town = models.ForeignKey(Town)
	location_url = models.CharField(max_length=300, blank=True)
	picture = models.CharField(max_length=100, blank=True)

	def __unicode__(self):
		return self.name

class BreweryForm(ModelForm):
	class Meta:
		model = Brewery
		exclude = ('description', 'location_url', 'picture')

class Type(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True, null=True)
	
	def __unicode__(self):
		return self.name

class Beer(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True, null=True)
	picture = models.CharField(max_length=100, blank=True)
	type = models.ForeignKey(Type)
	brewery = models.ForeignKey(Brewery)
	abv = models.DecimalField(max_digits=4, decimal_places=2, default=0)
	sb_id = models.IntegerField(default=0)

	def __unicode__(self):
		return self.name

class BeerForm(ModelForm):
	class Meta:
		model = Beer
		exclude = ('description', 'picture')

class Review(ContentStreamItem):
	beer = models.ForeignKey(Beer)
	text = models.TextField(blank=True, null=True)
	score = models.IntegerField(default=0)
	affordability_index = models.DecimalField(max_digits=4, decimal_places=2, default=0)
	official = models.BooleanField(default=False)

	def __unicode__(self):
		return "Review of: " + self.beer.name

class BeerIngredient(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True, null=True)
	country = models.ForeignKey(Country)

	class Meta:
		abstract = True

class HopsType(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True, null=True)
	alpha_contrib = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	
	def __unicode__(self):
		return self.name

class Hops(BeerIngredient):
	alpha = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	HOPS_TYPES = (
		(u'cones', u'Kottar'),
		(u'pellets', u'Pellets'),
	)
	hops_type = models.CharField(max_length=10, choices=HOPS_TYPES, default='cones')

	def __unicode__(self):
		return u'%s, %f.2%%' % (self.name, self.alpha)

class MaltType(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True, null=True)
	extract_potential = models.IntegerField(default=0)

	def __unicode__(self):
		return self.name

class Malt(BeerIngredient):
	ebc = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	dbfg = models.DecimalField(max_digits=5, decimal_places=2, default=0)
	mc = models.DecimalField(max_digits=5, decimal_places=2, default=0)
	protein = models.DecimalField(max_digits=5, decimal_places=2, default=0)
	malt_type = models.ForeignKey(MaltType)

	def __unicode__(self):
		return self.name

class YeastType(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True, null=True)
	
	def __unicode__(self):
		return self.name

class Yeast(BeerIngredient):
	fermentation_temp_min = models.IntegerField(default=0)
	fermentation_temp_max = models.IntegerField(default=0)
	ideal_temp_min = models.IntegerField(default=0)
	ideal_temp_max = models.IntegerField(default=0)
	alcohol_tolerance = models.IntegerField(default=0)
	YEAST_TYPES = (
		(u'dry', u'Torr'),
		(u'liquid', u'Flytande'),
	)
	yeast_type = models.CharField(max_length=10, choices=YEAST_TYPES, default='dry')
	attenuation = models.DecimalField(max_digits=3, decimal_places=1, default=0)
	cell_concentration = models.DecimalField(u"miljarder jästceller/g", max_digits=5, decimal_places=3, default=0)
	FLOCCULATION_TYPES = (
		(u'low', u'Låg'),
		(u'medium', u'Medium'),
		(u'high', u'Hög'),
	)
	flocculation = models.CharField(max_length=10, choices=FLOCCULATION_TYPES, default='medium')
	
	def __unicode__(self):
		return self.name

class MiscIngredient(BeerIngredient):
	extract_potential = models.IntegerField(default=0)
	
	def __unicode__(self):
		return self.name

class BeerRecipe(models.Model):
	beer = models.ForeignKey(Beer)
	start_water_volume = models.DecimalField(u"start vattenvolym", max_digits=4, decimal_places=2, default=0)
	final_volume = models.DecimalField(u"slutvolym", max_digits=4, decimal_places=2, default=0)
	mash_in_temp = models.IntegerField(u"inmäskningstemperatur", default=0)
	mashing_temp = models.IntegerField(u"mäskningstemperatur", default=0)
	mashing_time = models.IntegerField(u"mäskningstid", default=0)
	mash_out_temp = models.IntegerField(u"utmäskningstermperatur", default=0)
	mash_out_time = models.IntegerField(u"utmäskningstid", default=0)
	conversion_efficiency = models.IntegerField(u"konverteringseffektivitet", default=100)
	lauter_efficiency = models.IntegerField(u"lakningseffektivitet", default=100)
	pre_lauter_sg = models.DecimalField(u"SG innan lakning", max_digits=4, decimal_places=3, default=0)
	pre_boil_sg = models.DecimalField(u"SG innan kok", max_digits=4, decimal_places=3, default=0)
	og = models.DecimalField(u"OG", max_digits=4, decimal_places=3, default=0)
	fg = models.DecimalField(u"FG", max_digits=4, decimal_places=3, default=0)
	secret = models.BooleanField(default=False)
	creator = models.ForeignKey(User)
	group = models.ForeignKey(Group, null=True, blank=True)
	
	class Meta:
		permissions = (
			("view_recipe", "Can view recipe"),
			("view_secret_recipe", "Can view secret recipe"),
		)

	def __unicode__(self):
		return u'Recipe: %s, %d l' % (self.beer.name, self.final_volume)

class BeerRecipeForm(ModelForm):
	class Meta:
		model = BeerRecipe
		exclude = ('beer', 'secret', 'creator', 'group')

class NewBeerRecipeForm(ModelForm):
	class Meta:
		model = BeerRecipe
		fields = ('beer', 'secret', 'creator', 'group')

class HopsRecipeEntry(models.Model):
	recipe = models.ForeignKey(BeerRecipe)
	hops = models.ForeignKey(Hops)
	amount = models.IntegerField(default=0)
	add_time = models.IntegerField(default=0)

	def __unicode__(self):
		return u'%s: %s %d g, %d min' % (self.recipe.beer.name, self.hops.name, self.amount, self.add_time)

	def render(self):
		return u'%s %d g, %d min' % (self.hops.name, self.amount, self.add_time)

class MaltRecipeEntry(models.Model):
	recipe = models.ForeignKey(BeerRecipe)
	malt = models.ForeignKey(Malt)
	amount = models.DecimalField(max_digits=4, decimal_places=1, default=0)
	
	def __unicode__(self):
		return u'%s: %s %f g' % (self.recipe.beer.name, self.malt.name, self.amount)

	def render(self):
		return u'%s %d g, %d min' % (self.malt.name, self.amount, self.add_time)

class MiscIngredientEntry(models.Model):
	recipe = models.ForeignKey(BeerRecipe)
	ingredient = models.ForeignKey(MiscIngredient)
	amount = models.IntegerField(default=0)
	add_time = models.IntegerField(default=0)

	def __unicode__(self):
		return u'%s: %s %d g, %d min' % (self.recipe.beer.name, self.ingredient.name, self.amount, self.add_time)

class PrimaryFermentation(models.Model):
	recipe = models.ForeignKey(BeerRecipe)
	temp = models.IntegerField(default=0)
	time = models.DecimalField(max_digits=4, decimal_places=1, default=0)
	yeast = models.ForeignKey(Yeast, null=True, blank=True)
	yeast_amount = models.DecimalField(max_digits=4, decimal_places=1, default=0)
	TARGET_PITCH_TYPE = (
		(Decimal(0.35), u'Tillverkare'),
		(Decimal(0.5), u'Tillverkare 1.060+'),
		(Decimal(0.75), u'Ale'),
		(Decimal(1.0), u'Ale 1.060+'),
		(Decimal(1.5), u'Lager'),
		(Decimal(2.0), u'Lager 1.060+'),
	)
	target_pitch_rate = models.DecimalField(max_digits=4, decimal_places=2, default=0.75, choices=TARGET_PITCH_TYPE)

	def __unicode__(self):
		return u'%s: %d dagar' % (self.recipe.beer.name, self.time)

class SecondaryFermentation(models.Model):
	recipe = models.ForeignKey(BeerRecipe)
	temp = models.IntegerField(default=0)
	time = models.DecimalField(max_digits=4, decimal_places=1, default=0)

	def __unicode__(self):
		return u'%s: %d dagar' % (self.recipe.beer.name, self.time)

class DryHoppingRecipeEntry(models.Model):
	fermentation_stage = models.ForeignKey(SecondaryFermentation)
	hops = models.ForeignKey(Hops)
	amount = models.IntegerField(default=0)

	def __unicode__(self):
		return u'%s: %s %d g, %d min' % (self.fermentation_stage.recipe.beer.name, self.hops.name, self.amount)

class ExtraFlavourRecipeEntry(models.Model):
	fermentation_stage = models.ForeignKey(SecondaryFermentation)
	ingredient = models.ForeignKey(MiscIngredient)
	amount = models.IntegerField(default=0)
	
	def __unicode__(self):
		return u'%s: %s %d g, %d min' % (self.fermentation_stage.recipe.beer.name, self.ingredient.name, self.amount)

class PrimingEntry(models.Model):
	recipe = models.ForeignKey(BeerRecipe)
	SUGAR_TYPES = (
		(Decimal(0.35), u'Corn Sugar'),
		(Decimal(0.5), u'Anhydrous Glucose'),
		(Decimal(0.75), u'Bordssocker'),
		(Decimal(1.0), u'Torkat maltextrakt'),
	)
	sugar_type = models.DecimalField(max_digits=4, decimal_places=2, default=0.75, choices=SUGAR_TYPES)
	sugar_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
	carbon_dioxide_concentration = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
	
	def __unicode__(self):
		return u'%s: Kolsyresättning' % (self.recipe.beer.name)
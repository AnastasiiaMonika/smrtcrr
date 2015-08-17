{-# LANGUAGE OverloadedStrings #-}
module Main (main) where

import Control.Applicative ((<$>))
import Control.Monad (forM)
import Data.Char
import Data.List

import Data.Monoid --union
import Data.Foldable (fold)

import Control.Exception

import qualified Data.Map.Strict as M

import Network.HTTP.Conduit

import qualified Data.ByteString.Lazy.Char8 as BL
import qualified Data.ByteString.Char8 as BS
import qualified Data.Text as TS
import qualified Data.Text.Lazy as T
import qualified Data.Text.Lazy.Encoding as E

import Text.HTML.TagSoup

import Control.Lens ((^..))
import Data.Aeson.Lens

-- link = "http://www.nytimes.com/2015/07/31/world/europe/us-names-new-targets-of-sanctions-over-ukraine.html?ref=topics&_r=0"
-- link = "http://www.nytimes.com//2015//08//02//travel//poland-jewish-heritage.html"

data Score = Score { sGood :: !Int, sBad :: !Int } deriving (Show, Eq)

instance Monoid Score where
	mempty = Score 0 0
	mappend (Score p1 n1) (Score p2 n2) = Score (p1 + p2) (n1 + n2)

catchAll :: IO a -> (SomeException -> IO a) -> IO a
catchAll = Control.Exception.catch

nyTimesKey = "9de29e78390e1127f01f5d7301c0adb3:19:72608615"

good = ["bronze", "democratic", "nadezhda", "power", "stabilization", "support", "win", "won"]
bad = ["arrested", "blamed", "denied", "failing", "indignities", "negative", "war", "crisis"]

main = do
	urls <- getUrlsFor 10 "Ukraine"
	contexts <- forM urls $ \url' -> (do
		let url = TS.unpack url'
		putStrLn $ "Trying url: " ++ url
		res <- getContextWordsFromPage 3 "ukrain" url
		putStr "Result: " >> print res
		return res) `catchAll` const (return M.empty)

	let res = foldr mergeCounts M.empty contexts
	print $ sort . fmap (\(x, y) -> (y, x)) . M.toList $ res
	print (score res)

s :: String -> String
s = id

score :: M.Map T.Text Int -> Score
score = Data.Foldable.fold . M.mapMaybeWithKey f
	where
		f key value
			| key `elem` good = Just $ Score value 0
			| key `elem` bad  = Just $ Score 0 value
			| otherwise       = Nothing

getUrlsFor :: Int -> BS.ByteString -> IO [TS.Text]
getUrlsFor count term = do
	let url = "http://api.nytimes.com/svc/search/v2/articlesearch.json"
	let params =
		[ ("q", Just term)
		, ("sort", Just "newest")
		, ("fl", Just "web_url")
		, ("api-key", Just nyTimesKey)
		]
	request <- setQueryString params <$> parseUrl url
	response <- withManager $ httpLbs request
	return $ responseBody response ^.. key "response" . key "docs" . values . key "web_url" . _String

getContextWordsFromPage :: Int -> T.Text -> String -> IO (M.Map T.Text Int)
getContextWordsFromPage n word url = countContextWords n word . getText . E.decodeUtf8 <$> simpleHttp url

countContextWords :: Int -> T.Text -> T.Text -> M.Map T.Text Int
countContextWords n word = count . concat . findContext n word . dropSigns

getText :: T.Text -> T.Text
getText = innerText . dropAside . takeWhile (~/= s "<footer>") . dropWhile (~/= s "<p class=\"story-body-text story-content\"") . parseTags
	where
		dropAside x = beforeAside ++ afterAside
			where
				beforeAside = takeWhile (~/= s "<aside>") x
				afterAside = dropWhile (~/= s "</aside>") x

dropSigns :: T.Text -> T.Text
dropSigns = T.map f
	where
		f x
			| isAlpha x = toLower x
			| otherwise = ' '

findContext :: Int -> T.Text -> T.Text -> [[T.Text]]
findContext n word t = fmap (\(x, _, y) -> take n x ++ take n y) . filter (\(_, x, _) -> word `T.isInfixOf` x) $ withContext w
	where w = T.words t

withContext :: [a] -> [([a], a, [a])]
withContext = withContext' []
	where
		withContext' _    []     = []
		withContext' prev (x:xs) = (prev, x, xs) : withContext' (x:prev) xs

count :: Ord a => [a] -> M.Map a Int
count = foldr f M.empty
	where f k m = M.insertWith (+) k 1 m

mergeCounts :: Ord a => M.Map a Int -> M.Map a Int -> M.Map a Int
mergeCounts = M.unionWith (+)